import asyncio
import queue
import threading
import time

from stt.vad import get_speech_frames
from stt.whisper import transcribe
from core.brain import handle
from tts.voice import speak

from core.audio_state import audio_state
from core.shutdown import is_shutdown, trigger_shutdown


# =========================================================
# EVENT BUS
# =========================================================
audio_queue = queue.Queue()
tts_queue = queue.Queue()

system_busy = threading.Event()


# =========================================================
# TTS ENGINE (INTERRUPTIBLE CORE)
# =========================================================
def tts_worker():

    while not is_shutdown():

        try:
            text = tts_queue.get(timeout=0.5)
        except queue.Empty:
            continue

        if text is None:
            break

        try:
            system_busy.set()

            audio_state.start_speaking(hold_seconds=1.5)

            print(f"[JARVIS TTS] {text}")

            speak(text)

        finally:
            audio_state.stop_speaking()
            system_busy.clear()
            tts_queue.task_done()

    print("[TTS] EXIT")


# =========================================================
# COGNITIVE ENGINE (STREAM LOOP)
# =========================================================
async def cognitive_loop():

    while not is_shutdown():

        try:
            audio = await asyncio.to_thread(audio_queue.get, True, 0.5)
        except queue.Empty:
            continue

        if audio is None:
            break

        # ignore audio while speaking
        if system_busy.is_set():
            continue

        try:
            text = await asyncio.to_thread(transcribe, audio)

            if not text:
                continue

            print(f"[HEARD] {text}")

            response = handle(text)

            if response:
                print(f"[JARVIS] {response}")
                tts_queue.put(response)

        except Exception as e:
            print(f"[PIPELINE ERROR] {e}")


# =========================================================
# VAD PRODUCER
# =========================================================
def vad_loop():

    try:
        for audio in get_speech_frames():

            if is_shutdown():
                break

            audio_queue.put(audio)

    finally:
        print("[VAD] EXIT")


# =========================================================
# KERNEL START
# =========================================================
def start_kernel():

    print("[SYSTEM] BOOTING JARVIS ALIVE CORE v3")
    print("[SYSTEM] EVENT KERNEL ACTIVE\n")

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

        time.sleep(0.5)

        print("[SYSTEM] KERNEL SHUTDOWN COMPLETE")