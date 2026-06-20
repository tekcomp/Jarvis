import os
import sys
import time

from stt.whisper import transcribe
from stt.vad import get_speech_frames
from core.brain import handle
from tts.voice import speak, is_speaking

# ensure root path
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

try:
    from core.logger import L1, L3
except Exception:
    def L1(msg):
        print(msg)

    def L3(msg):
        print(msg)


def main():
    print("[SYSTEM] BOOTING JARVIS CORE")
    L3("VAD LOOP START")

    last_time = 0
    MIN_GAP = 0.8

    for audio in get_speech_frames():

        try:
            # 🔥 CRITICAL: block mic during TTS playback
            if is_speaking():
                continue

            # debounce VAD spam
            now = time.time()
            if now - last_time < MIN_GAP:
                continue

            L3("AUDIO RECEIVED")

            text = transcribe(audio)

            if not text:
                L3("FILTER: empty transcription")
                continue

            print(f"[HEARD] {text}")

            response = handle(text)

            if not response:
                L3("FILTER: no response")
                continue

            print(f"[JARVIS] {response}")

            speak(response)

            last_time = time.time()

        except KeyboardInterrupt:
            raise

        except Exception as e:
            print(f"[MAIN ERROR] {e}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[SYSTEM] SAFE SHUTDOWN")