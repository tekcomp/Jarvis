from stt.vad import get_speech_frames
from stt.whisper import transcribe
from core.brain import handle
from tts.voice import speak

from core.logger import L3
import threading
import time


# -------------------------
# GLOBAL EXECUTION GUARD
# -------------------------
tts_lock = threading.Lock()
pipeline_lock = threading.Lock()


def safe_speak(text: str):
    """
    Hard-safe TTS wrapper:
    - prevents overlap
    - ensures mic suppression state is respected
    - prevents double execution
    """

    if not text:
        return

    # prevent multiple concurrent TTS calls
    if not tts_lock.acquire(blocking=False):
        return

    try:
        speak(text)
        time.sleep(0.2)  # recovery buffer for mic release
    finally:
        if tts_lock.locked():
            tts_lock.release()


def safe_pipeline(audio):
    """
    Ensures only one STT → brain → TTS pipeline runs at a time
    prevents race conditions from fast VAD bursts
    """

    with pipeline_lock:

        L3("AUDIO RECEIVED FROM VAD")

        # -------------------------
        # TRANSCRIBE
        # -------------------------
        text = transcribe(audio)

        if not text:
            L3("WHISPER EMPTY")
            return

        print(f"[HEARD] {text}")

        # -------------------------
        # INTENT ENGINE
        # -------------------------
        response = handle(text)

        if not response:
            return

        print(f"[JARVIS] {response}")

        # -------------------------
        # TTS (blocking inside safe wrapper)
        # -------------------------
        safe_speak(response)


def main():

    print("[SYSTEM] BOOTING JARVIS CORE")
    print("[SYSTEM] LISTENING...\n")

    try:
        for audio in get_speech_frames():
            try:
                safe_pipeline(audio)

            except Exception as e:
                print(f"[PIPELINE ERROR] {e}")

    except KeyboardInterrupt:
        print("\n[SYSTEM] SHUTDOWN REQUESTED")


if __name__ == "__main__":
    main()