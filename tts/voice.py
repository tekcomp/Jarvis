import pyttsx3
import threading
import time

_lock = threading.Lock()


def speak(text: str):
    if not text:
        return

    if not _lock.acquire(blocking=False):
        return

    try:
        print("[TTS TEST] speaking:", text)

        # 🔥 CRITICAL FIX: fresh engine per call (Windows-safe)
        engine = pyttsx3.init()

        engine.setProperty("rate", 180)
        engine.setProperty("volume", 1.0)

        engine.say(text)
        engine.runAndWait()

        # HARD cleanup (prevents silent deadlock)
        engine.stop()
        del engine

        time.sleep(0.1)

        print("[TTS TEST] done")

    except Exception as e:
        print(f"[TTS ERROR] {e}")

    finally:
        _lock.release()