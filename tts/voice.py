import sounddevice as sd
from kokoro import KPipeline
import state
import config
import threading

pipeline = KPipeline(lang_code="a", device="cpu")


def _play(gen):
    state.state.speaking = True
    state.state.stop_speaking = False

    for _, _, audio in gen:
        if state.state.stop_speaking:
            sd.stop()
            break

        sd.play(audio, 24000)
        sd.wait()

    state.state.speaking = False


def speak(text):

    gen = pipeline(text=text, voice=config.VOICE)

    threading.Thread(target=_play, args=(gen,), daemon=True).start()