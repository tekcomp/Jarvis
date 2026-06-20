import pyttsx3
import numpy as np


def synthesize_audio(text: str, samplerate: int = 24000):
    """
    Stable pyttsx3 TTS engine (FIXED silent drop issue)
    """

    if not text:
        return np.zeros(int(samplerate * 0.1), dtype=np.float32)

    # 🔥 create fresh engine each time (fixes silent failures)
    engine = pyttsx3.init()

    engine.setProperty('rate', 175)
    engine.setProperty('volume', 1.0)

    try:
        engine.say(text)
        engine.runAndWait()
    except Exception as e:
        print(f"[TTS ERROR] {e}")

    finally:
        try:
            engine.stop()
        except:
            pass

    # dummy return (keeps compatibility with your pipeline)
    return np.zeros(int(samplerate * 0.1), dtype=np.float32)