from stt.vad import get_speech_frames
from stt.whisper import transcribe
from core.brain import handle
from tts.voice import speak

from core.logger import L3
from core.audio_state import audio_state

import threading
import time


# =========================================================
# SINGLE STATE CONTROL (ONLY TRUTH SOURCE)
# =========================================================
system_busy = threading.Event()


# =========================================================
# TTS EXECUTION (NO EXTRA LOCKS)
# =========================================================
def safe_speak(text: str):
    if not text:
        return

    try:
        system_busy.set()

        audio_state.start_speaking(hold_seconds=2.0)

        print(f"[JARVIS TTS] {text}")

        speak(text)   # MUST handle blocking internally

    except Exception as e:
        print(f"[TTS ERROR] {e}")

    finally:
        try:
            audio_state.stop_speaking()
        except:
            pass

        time.sleep(0.1)
        system_busy.clear()


# =========================================================
# PIPELINE (NO LOCKS — DROP OLD AUDIO ONLY)
# =========================================================
def safe_pipeline(audio):

    # drop audio while speaking
    if system_busy.is_set():
        return

    try:
        L3("AUDIO RECEIVED FROM VAD")

        text = transcribe(audio)

        if not text:
            L3("WHISPER EMPTY")
            return

        print(f"[HEARD] {text}")

        response = handle(text)

        if not response:
            return

        print(f"[JARVIS] {response}")

        safe_speak(response)

    except Exception as e:
        print(f"[PIPELINE ERROR] {e}")


# =========================================================
# MAIN LOOP
# =========================================================
def main():

    print("[SYSTEM] BOOTING JARVIS CORE")
    print("[SYSTEM] LISTENING...\n")

    try:
        for audio in get_speech_frames():

            # drop VAD noise during speaking
            if system_busy.is_set():
                continue

            safe_pipeline(audio)

    except KeyboardInterrupt:
        print("\n[SYSTEM] SHUTDOWN REQUESTED")

    except Exception as e:
        print(f"[FATAL ERROR] {e}")


if __name__ == "__main__":
    main()