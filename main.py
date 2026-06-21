import asyncio
import threading
import queue

from stt.vad import get_speech_frames
from stt.whisper import transcribe
from core.brain import handle
from tts.voice import speak

from core.logger import L3
from core.audio_state import audio_state
from core.shutdown import trigger_shutdown, is_shutdown


# =========================================================
# QUEUES
# =========================================================
audio_queue = queue.Queue()
tts_queue = queue.Queue()

system_busy = threading.Event()


# =========================================================
# TTS WORKER
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

            audio_state.start_speaking(hold_seconds=2.0)

            print(f"[JARVIS TTS] {text}")

            speak(text)

        finally:
            try:
                audio_state.stop_speaking()
            except Exception:
                pass

            system_busy.clear()

            try:
                tts_queue.task_done()
            except Exception:
                pass

    print("[TTS] EXIT")


# =========================================================
# COGNITIVE LOOP
# =========================================================
async def cognitive_loop():

    while not is_shutdown():

        try:
            audio = await asyncio.to_thread(audio_queue.get, True, 0.5)
        except queue.Empty:
            continue

        if audio is None:
            break

        try:
            L3("AUDIO RECEIVED")

            if len(audio) < 2000:
                continue

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

    print("[COGNITIVE] EXIT")


# =========================================================
# VAD THREAD
# =========================================================
def vad_producer():

    try:
        for audio in get_speech_frames():

            if is_shutdown():
                break

            audio_queue.put(audio)

    finally:
        print("[VAD] EXIT")


# =========================================================
# MAIN
# =========================================================
def main():
    warmup_whisper()

    print("[SYSTEM] BOOTING JARVIS COGNITIVE LOOP v2")
    print("[SYSTEM] STREAMING MODE ACTIVE\n")

    vad_thread = threading.Thread(target=vad_producer)
    tts_thread = threading.Thread(target=tts_worker)

    vad_thread.start()
    tts_thread.start()

    try:
        asyncio.run(cognitive_loop())

    except KeyboardInterrupt:
        trigger_shutdown("keyboard interrupt")

    except Exception as e:
        trigger_shutdown(f"fatal error: {e}")

    finally:

        trigger_shutdown("main exit")

        audio_queue.put(None)
        tts_queue.put(None)

        # HARD JOIN (NO SLEEP)
        vad_thread.join(timeout=2)
        tts_thread.join(timeout=2)

        print("[SYSTEM] SHUTDOWN COMPLETE")
        
# =========================================================
# WARMUP WHISPER
# =========================================================
def warmup_whisper():
    try:
        import numpy as np
        from stt.whisper import transcribe

        silent = np.zeros(16000, dtype=np.int16)

        _ = transcribe(silent)

    except:
        pass
if __name__ == "__main__":
    main()