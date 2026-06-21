from stt.vad import get_speech_frames
from stt.whisper import transcribe
from core.brain import handle
from tts.voice import speak

from core.logger import L3
from core.audio_state import audio_state

import threading
import time

# =========================================================
# SYSTEM LOCKS
# =========================================================

pipeline_lock = threading.Lock()
tts_lock = threading.Lock()

system_busy = threading.Event()


# =========================================================
# TTS WRAPPER (LOW LATENCY + SAFE)
# =========================================================
def safe_speak(text: str):
    if not text:
        return

    # avoid double TTS execution
    if not tts_lock.acquire(blocking=False):
        return

    try:
        system_busy.set()

        # activate mic suppression BEFORE TTS
        audio_state.start_speaking(hold_seconds=2.0)

        print(f"[JARVIS TTS] {text}")

        speak(text)

    except Exception as e:
        print(f"[TTS ERROR] {e}")

    finally:
        # ALWAYS release mic + system state
        try:
            audio_state.stop_speaking()
        except Exception:
            pass

        system_busy.clear()

        time.sleep(0.15)  # reduced latency buffer

        tts_lock.release()


# =========================================================
# PIPELINE (DROP-OLD AUDIO MODEL)
# =========================================================
def safe_pipeline(audio):

    # CRITICAL: drop audio while speaking
    if system_busy.is_set():
        return

    # prevent pipeline stacking
    if not pipeline_lock.acquire(blocking=False):
        return

    try:
        L3("AUDIO RECEIVED FROM VAD")

        # -------------------------
        # STT
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
        # TTS
        # -------------------------
        safe_speak(response)

    except Exception as e:
        print(f"[PIPELINE ERROR] {e}")

    finally:
        pipeline_lock.release()


# =========================================================
# MAIN LOOP
# =========================================================
def main():

    print("[SYSTEM] BOOTING JARVIS CORE")
    print("[SYSTEM] LISTENING...\n")

    try:
        for audio in get_speech_frames():

            # extra safety: ignore stale audio during speech
            if system_busy.is_set():
                continue

            safe_pipeline(audio)

    except KeyboardInterrupt:
        print("\n[SYSTEM] SHUTDOWN REQUESTED")

    except Exception as e:
        print(f"[FATAL ERROR] {e}")


if __name__ == "__main__":
    main()