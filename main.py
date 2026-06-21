from stt.vad import get_speech_frames
from stt.whisper import transcribe
from core.brain import handle
from tts.voice import speak

from core.logger import L3
from core.audio_state import audio_state
import threading
import time


# -------------------------
# TTS EXECUTION LOCK
# -------------------------
tts_lock = threading.Lock()


def safe_speak(text: str):
    """
    Single-threaded TTS execution with proper echo suppression sync
    """

    if not text:
        return

    # prevent overlapping speech
    if tts_lock.locked():
        return

    with tts_lock:

        try:
            speak(text)

        finally:
            # small recovery window ensures mic re-enables cleanly
            time.sleep(0.15)


def main():

    print("[SYSTEM] BOOTING JARVIS CORE")
    print("[SYSTEM] LISTENING...\n")

    for audio in get_speech_frames():

        try:

            L3("AUDIO RECEIVED FROM VAD")

            # -------------------------
            # TRANSCRIBE
            # -------------------------
            text = transcribe(audio)

            if not text:
                L3("WHISPER EMPTY")
                continue

            print(f"[HEARD] {text}")

            # -------------------------
            # BRAIN PROCESSING
            # -------------------------
            response = handle(text)

            if response:

                print(f"[JARVIS] {response}")

                safe_speak(response)

        except Exception as e:
            print(f"[MAIN ERROR] {e}")


if __name__ == "__main__":
    main()