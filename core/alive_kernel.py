# ==============================
# core/alive_kernel.py (JARVIS STABLE v7 - FINAL FIX)
# ==============================

import asyncio
import queue
import threading
import time

from stt.vad import get_speech_frames
from stt.whisper import transcribe
from core.brain import stream_response
from tts.voice import speak

from core.runtime_state import system_busy
from core.shutdown import is_shutdown, trigger_shutdown
from core.interruption import is_interrupted

from core.interrupt_fsm import InterruptFSM
from core.spec_contract_v2 import SpecContractV2, Intent


# =========================================================
# FSM (SINGLE SOURCE OF TRUTH)
# =========================================================
fsm = InterruptFSM()

audio_queue = queue.Queue()
tts_queue = queue.Queue()


# =========================================================
# ANTI-ECHO CONTROL
# =========================================================
TTS_ACTIVE = False
IGNORE_UNTIL = 0


def enter_tts_state():
    global TTS_ACTIVE, IGNORE_UNTIL
    TTS_ACTIVE = True

    # HARD AUDIO LOCK WINDOW
    IGNORE_UNTIL = time.time() + 1.3


def exit_tts_state():
    global TTS_ACTIVE
    TTS_ACTIVE = False


def is_echo_window():
    return time.time() < IGNORE_UNTIL


# =========================================================
# INTENT ROUTER (CRITICAL FIX)
# =========================================================
def route_intent(text: str):

    contract = SpecContractV2.classify(text)

    if contract.intent == Intent.TIME:
        import datetime
        return f"The time is {datetime.datetime.now().strftime('%H:%M:%S')}."

    if contract.intent == Intent.DATE:
        import datetime
        return f"Today is {datetime.datetime.now().strftime('%A, %B %d, %Y')}."

    if contract.intent == Intent.JOKE:
        return "Why did the AI cross the road? To optimize the reward function."

    # fallback goes to brain
    return None


# =========================================================
# TTS ENGINE
# =========================================================
def tts_worker():

    fsm.start_tts()

    while not is_shutdown():

        try:
            text = tts_queue.get(timeout=0.3)
        except queue.Empty:
            continue

        if text is None:
            break

        system_busy.set()
        enter_tts_state()

        try:
            print(f"[JARVIS TTS] {text}")
            speak(text)
        finally:
            system_busy.clear()
            exit_tts_state()
            tts_queue.task_done()

    print("[TTS] EXIT")
    fsm.stop_tts()


# =========================================================
# COGNITIVE ENGINE
# =========================================================
async def cognitive_loop():

    print("[CI-BOOT] cognitive_loop STARTED")

    frame_id = 0

    while not is_shutdown():

        try:
            packet = audio_queue.get(timeout=0.5)
        except queue.Empty:
            await asyncio.sleep(0.03)
            continue

        if packet is None:
            break

        if is_echo_window():
            print("[CI-ECHO] IGNORED AUDIO WINDOW")
            continue

        audio = packet.get("audio")

        if not audio:
            continue

        frame_id += 1

        text = transcribe(audio)

        if not text:
            continue

        print(f"[CI-FSM] HEARD: {text}")

        # =====================================================
        # INTENT FIRST (CRITICAL FIX)
        # =====================================================
        direct = route_intent(text)

        if direct:
            print(f"[CI-ROUTER] DIRECT RESPONSE: {direct}")
            tts_queue.put(direct)
            continue

        # =====================================================
        # FALLBACK TO STREAM ENGINE
        # =====================================================
        final_text = ""

        for chunk in stream_response(text):

            if is_interrupted():
                final_text = ""
                break

            final_text += chunk

        if final_text and not is_interrupted():
            print(f"[CI-TTS] QUEUE_PUSH: {final_text}")
            tts_queue.put(final_text)


# =========================================================
# VAD LOOP (FIXED STABILITY)
# =========================================================
def vad_loop():

    frame_id = 0

    try:
        for audio in get_speech_frames():

            frame_id += 1

            if is_echo_window():
                continue

            if audio is None:
                continue

            # SAFE DETECTION
            try:
                speaking = len(audio) > 0
            except Exception:
                speaking = False

            fsm.evaluate(frame_id, speaking)

            if speaking:
                audio_queue.put({
                    "frame_id": frame_id,
                    "audio": audio
                })

                print("[CI-VAD] AUDIO PUSHED")

            if is_shutdown():
                break

    finally:
        print("[VAD] EXIT")


# =========================================================
# START KERNEL
# =========================================================
def start_kernel():

    print("[SYSTEM] BOOTING JARVIS CORE v3.1")
    print("[SYSTEM] INTERRUPT FSM MODE ACTIVE")

    threading.Thread(target=vad_loop, daemon=True).start()
    threading.Thread(target=tts_worker, daemon=True).start()

    try:
        asyncio.run(cognitive_loop())

    except KeyboardInterrupt:
        trigger_shutdown("keyboard interrupt")

    finally:
        trigger_shutdown("kernel exit")

        audio_queue.put(None)
        tts_queue.put(None)

        fsm.stop_tts()
        fsm.fired = False

        print("[SYSTEM] SHUTDOWN COMPLETE")