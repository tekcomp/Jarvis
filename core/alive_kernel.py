# ==============================
# core/alive_kernel.py (ANTI-ECHO LOOP FIX v6)
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


# =========================================================
# GLOBAL FSM
# =========================================================
fsm = InterruptFSM()

audio_queue = queue.Queue()
tts_queue = queue.Queue()


# =========================================================
# ANTI-ECHO SYSTEM (CRITICAL FIX)
# =========================================================
TTS_ACTIVE = False
interrupt_token = 1
interrupt_locked = False

# 🚨 NEW: echo suppression window
IGNORE_AUDIO_UNTIL = 0


def reset_interrupt_state():
    global interrupt_token, interrupt_locked
    interrupt_token = 1
    interrupt_locked = False


def enter_tts_state():
    global TTS_ACTIVE, IGNORE_AUDIO_UNTIL

    TTS_ACTIVE = True
    reset_interrupt_state()

    # 🚨 CRITICAL FIX: ignore mic during TTS playback + buffer tail
    IGNORE_AUDIO_UNTIL = time.time() + 1.2


def exit_tts_state():
    global TTS_ACTIVE
    TTS_ACTIVE = False


def should_ignore_audio():
    return time.time() < IGNORE_AUDIO_UNTIL


def try_interrupt():
    global interrupt_token, interrupt_locked

    if not system_busy.is_set():
        return
    if not TTS_ACTIVE:
        return
    if interrupt_locked:
        return

    interrupt_locked = True
    interrupt_token = 0

    try:
        from core.audio_state import audio_state
        audio_state.on_interrupt()
    except Exception:
        pass


# =========================================================
# TTS ENGINE
# =========================================================
def tts_worker():

    fsm.start_tts()

    while not is_shutdown():

        try:
            text = tts_queue.get(timeout=0.5)
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

        print("[CI-DEBUG] waiting for audio...")

        try:
            packet = audio_queue.get(timeout=0.5)
        except queue.Empty:
            await asyncio.sleep(0.03)
            continue

        if packet is None:
            break

        audio = packet.get("audio")

        if audio is None:
            continue

        # 🚨 CRITICAL FIX: ignore self-echo / TTS leakage
        if should_ignore_audio():
            print("[CI-ECHO] IGNORED AUDIO (TTS WINDOW)")
            continue

        frame_id += 1

        print(f"[CI-AUDIO] RECEIVED frame={packet.get('frame_id')}")

        text = transcribe(audio)

        if not text:
            continue

        # 🚨 SECOND FILTER: ignore echo phrases that match last output
        if TTS_ACTIVE:
            print("[CI-ECHO] BLOCKED POSSIBLE SELF AUDIO")
            continue

        print(f"[CI-FSM] frame={frame_id} HEARD text={text}")

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
# VAD LOOP
# =========================================================
def vad_loop():

    frame_id = 0

    try:
        for audio in get_speech_frames():

            frame_id += 1

            # 🚨 CRITICAL FIX: suppress VAD during TTS echo window
            if should_ignore_audio():
                continue

            if audio is None:
                continue

            user_speaking = len(audio) > 0

            fsm.evaluate(frame_id, user_speaking)

            if user_speaking:
                audio_queue.put({
                    "frame_id": frame_id,
                    "audio": audio
                })

                print("[CI-VAD] AUDIO PUSHED")

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