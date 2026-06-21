from stt.vad import get_speech_frames
from stt.whisper import transcribe
from core.brain import handle
from tts.voice import speak

from core.logger import L3
from core.audio_state import audio_state

import threading
import time
import re

# =========================================================
# SYSTEM LOCKS
# =========================================================
pipeline_lock = threading.Lock()
tts_lock = threading.Lock()
system_busy = threading.Event()


# =========================================================
# INPUT NORMALIZER (NEW CRITICAL LAYER)
# =========================================================
def normalize_text(text: str) -> str:
    if not text:
        return ""

    text = text.lower().strip()

    # remove repeated consecutive words (basic de-dupe)
    words = text.split()
    deduped = []
    for w in words:
        if not deduped or deduped[-1] != w:
            deduped.append(w)
    text = " ".join(deduped)

    # remove non-ascii noise (foreign scripts, broken whisper fragments)
    if re.search(r"[^\x00-\x7F]+", text):
        return ""

    # ignore very short garbage
    if len(text.strip()) < 3:
        return ""

    return text


# =========================================================
# TTS WRAPPER
# =========================================================
def safe_speak(text: str):
    if not text:
        return

    if not tts_lock.acquire(blocking=False):
        return

    try:
        system_busy.set()

        audio_state.start_speaking(hold_seconds=2.0)

        print(f"[JARVIS TTS] {text}")

        speak(text)

    except Exception as e:
        print(f"[TTS ERROR] {e}")

    finally:
        try:
            audio_state.stop_speaking()
        except Exception:
            pass

        system_busy.clear()

        time.sleep(0.15)

        tts_lock.release()


# =========================================================
# PIPELINE
# =========================================================
def safe_pipeline(audio):

    if system_busy.is_set():
        return

    if not pipeline_lock.acquire(blocking=False):
        return

    try:
        L3("AUDIO RECEIVED FROM VAD")

        # -------------------------
        # STT
        # -------------------------
        text = transcribe(audio)

        # NEW: CLEAN INPUT BEFORE BRAIN
        text = normalize_text(text)

        if not text:
            L3("WHISPER EMPTY / NOISE FILTERED")
            return

        print(f"[HEARD] {text}")

        # -------------------------
        # BRAIN
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
            safe_pipeline(audio)

    except KeyboardInterrupt:
        print("\n[SYSTEM] SHUTDOWN REQUESTED")

    except Exception as e:
        print(f"[FATAL ERROR] {e}")


if __name__ == "__main__":
    main()