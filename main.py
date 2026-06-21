import asyncio
import threading
import time
import queue

from stt.vad import get_speech_frames
from stt.whisper import transcribe
from core.brain import handle
from tts.voice import speak

from core.logger import L3
from core.audio_state import audio_state


# =========================================================
# COGNITIVE QUEUES
# =========================================================
audio_queue = queue.Queue()
tts_queue = queue.Queue()

system_busy = threading.Event()


# =========================================================
# ASYNC TTS WORKER (NON-BLOCKING SPEECH ENGINE)
# =========================================================
def tts_worker():
    while True:
        text = tts_queue.get()

        if text is None:
            break

        try:
            system_busy.set()

            audio_state.start_speaking(hold_seconds=2.0)

            print(f"[JARVIS TTS] {text}")

            speak(text)

        except Exception as e:
            print(f"[TTS ERROR] {e}")

        finally:
            audio_state.stop_speaking()
            system_busy.clear()
            time.sleep(0.1)

        tts_queue.task_done()


# =========================================================
# STT + BRAIN PROCESSOR (ASYNC LOOP)
# =========================================================
async def cognitive_loop():

    while True:

        audio = await asyncio.to_thread(audio_queue.get)

        if audio is None:
            break

        try:
            L3("AUDIO RECEIVED")

            # STT (offload thread)
            text = await asyncio.to_thread(transcribe, audio)

            if not text:
                continue

            print(f"[HEARD] {text}")

            # BRAIN
            response = handle(text)

            if response:
                print(f"[JARVIS] {response}")
                tts_queue.put(response)

        except Exception as e:
            print(f"[PIPELINE ERROR] {e}")


# =========================================================
# VAD PRODUCER THREAD
# =========================================================
def vad_producer():
    for audio in get_speech_frames():
        audio_queue.put(audio)


# =========================================================
# MAIN ENTRY
# =========================================================
def main():

    print("[SYSTEM] BOOTING JARVIS COGNITIVE LOOP v2")
    print("[SYSTEM] STREAMING MODE ACTIVE\n")

    # start VAD thread
    threading.Thread(target=vad_producer, daemon=True).start()

    # start TTS worker
    threading.Thread(target=tts_worker, daemon=True).start()

    # start async cognitive loop
    asyncio.run(cognitive_loop())


if __name__ == "__main__":
    main()