# ==============================
# core/alive_kernel.py (AGENT v3 STABLE AUDIO GATED FIXED)
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
from core.audio_state import audio_state

from core.personality_engine_v2 import PersonalityEngineV2
from core.response_guard import ResponseGuard


# =========================================================
# COMPONENTS
# =========================================================
response_guard = ResponseGuard()
personality = PersonalityEngineV2()
fsm = InterruptFSM()

# =========================================================
# QUEUES
# =========================================================
audio_queue = queue.Queue()
tts_queue = queue.Queue()

# =========================================================
# GLOBAL STATE LOCKS
# =========================================================
UTTERANCE_LOCK = False
LAST_UTTERANCE = None
LAST_UTTERANCE_TS = 0
DUPLICATE_WINDOW_SEC = 2.5


# =========================================================
# SAFE AUDIO CHECK
# =========================================================
def has_audio(audio):
    if audio is None:
        return False
    try:
        return len(audio) > 0
    except Exception:
        return False


# =========================================================
# DUPLICATE DETECTION (FIXED SINGLE VERSION)
# =========================================================
def is_duplicate_utterance(text: str) -> bool:
    global LAST_UTTERANCE, LAST_UTTERANCE_TS

    now = time.time()

    if text == LAST_UTTERANCE and (now - LAST_UTTERANCE_TS) < DUPLICATE_WINDOW_SEC:
        return True

    LAST_UTTERANCE = text
    LAST_UTTERANCE_TS = now
    return False


# =========================================================
# TTS CONTROL
# =========================================================
def enter_tts():
    system_busy.set()
    audio_state.tts_started()


def exit_tts():
    system_busy.clear()
    audio_state.tts_finished()


# =========================================================
# UTTERANCE UNLOCK
# =========================================================
def unlock_utterance():
    global UTTERANCE_LOCK
    UTTERANCE_LOCK = False


# =========================================================
# TTS WORKER
# =========================================================
def tts_worker():

    fsm.start_tts()

    try:
        while not is_shutdown():

            if system_busy.is_set():
                time.sleep(0.05)
                continue

            try:
                text = tts_queue.get(timeout=0.5)
            except queue.Empty:
                continue

            if text is None:
                break

            enter_tts()

            try:
                print(f"[JARVIS TTS] {text}")
                print(f"[TTS TEST] speaking: {text}")

                speak(text)

            finally:
                exit_tts()
                tts_queue.task_done()
                print("[TTS TEST] done")

    finally:
        print("[TTS] EXIT")
        fsm.stop_tts()


# =========================================================
# COGNITIVE LOOP
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

        if not has_audio(audio):
            continue

        # HARD GATE (single authority)
        if not audio_state.mic_allowed():
            print("[CI-ECHO] BLOCKED BY AUDIO STATE")
            continue

        frame_id += 1

        print(f"[CI-AUDIO] RECEIVED frame={packet.get('frame_id')}")

        text = transcribe(audio)

        if not text or len(text.strip()) < 2:
            continue

        text = text.strip().lower()

        # duplicate filter
        if is_duplicate_utterance(text):
            print("[CI-GUARD] BLOCKED DUPLICATE INTENT")
            continue

        # utterance lock
        global UTTERANCE_LOCK
        if UTTERANCE_LOCK:
            continue

        UTTERANCE_LOCK = True

        # guard layer
        if response_guard.should_block(text):
            UTTERANCE_LOCK = False
            continue

        personality.update(text)

        print(f"[CI-FSM] frame={frame_id} HEARD text={text}")

        final_text = ""

        try:
            for chunk in stream_response(
                text,
                system_prompt=personality.system_prompt()
            ):

                if is_interrupted():
                    final_text = ""
                    break

                final_text += chunk

        finally:
            UTTERANCE_LOCK = False

        if final_text and not is_interrupted():
            print(f"[CI-TTS] QUEUE_PUSH: {final_text}")
            response_guard.update(text, final_text)

            tts_queue.put(final_text)

            # safety unlock fallback
            asyncio.get_event_loop().call_later(2.0, unlock_utterance)


# =========================================================
# VAD LOOP
# =========================================================
def vad_loop():

    frame_id = 0

    try:
        for audio in get_speech_frames():

            frame_id += 1

            if is_shutdown():
                break

            if not has_audio(audio):
                continue

            if not audio_state.mic_allowed():
                continue

            fsm.evaluate(frame_id, True)

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

    print("[SYSTEM] AGENT v3 BOOT")
    print("[SYSTEM] AUDIO GATE ENABLED")

    threading.Thread(target=vad_loop, daemon=True).start()
    threading.Thread(target=tts_worker, daemon=True).start()

    try:
        asyncio.run(cognitive_loop())

    except KeyboardInterrupt:
        trigger_shutdown("keyboard")

    finally:
        trigger_shutdown("exit")

        audio_queue.put(None)
        tts_queue.put(None)

        fsm.stop_tts()
        fsm.fired = False

        print("[SYSTEM] SHUTDOWN COMPLETE")