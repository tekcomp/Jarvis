import sounddevice as sd
from kokoro import KPipeline
import threading
import state

pipeline = KPipeline(lang_code="a", device="cpu")


def _play(gen):
    state.state.speaking = True
    state.state.stop_speaking = False

    try:
        for _, _, audio in gen:

            if state.state.stop_speaking:
                sd.stop()
                break

            sd.play(audio, 24000)
            sd.wait()

    finally:
        state.state.speaking = False


def speak(text: str):
    if not text:
        return

    gen = pipeline(text=text, voice="default")

    threading.Thread(target=_play, args=(gen,), daemon=True).start()