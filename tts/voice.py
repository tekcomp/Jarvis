import sounddevice as sd
from kokoro import KPipeline
import threading
import state
import time

pipeline = KPipeline(lang_code="a", device="cpu")
VOICE = "af_heart"


def _play(text: str):
    try:
        state.state.speaking = True
        state.state.ignore_audio = True

        gen = pipeline(text=text, voice=VOICE)

        for _, _, audio in gen:
            sd.play(audio, 24000)
            sd.wait()

    finally:
        time.sleep(0.4)
        state.state.speaking = False
        state.state.ignore_audio = False


def speak(text: str):
    if not text:
        return

    threading.Thread(target=_play, args=(text,), daemon=True).start()