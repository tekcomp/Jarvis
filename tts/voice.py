import sounddevice as sd
from kokoro import KPipeline
import threading
import state
import time

pipeline = KPipeline(lang_code="a", device="cpu")
VOICE = "af_heart"

def _play(text: str):
    try:
        state.state.ignore_audio = True   # 🔥 BLOCK MIC DURING SPEAKING

        gen = pipeline(text=text, voice=VOICE)

        for _, _, audio in gen:
            sd.play(audio, 24000)
            sd.wait()

    finally:
        time.sleep(0.5)
        state.state.ignore_audio = False
        state.state.speaking = False


def speak(text: str):
    if not text:
        return

    state.state.speaking = True
    threading.Thread(target=_play, args=(text,), daemon=True).start()