import sounddevice as sd
from kokoro import KPipeline
import threading
import state

pipeline = KPipeline(lang_code="a", device="cpu")

VOICE = "af_heart"

def _play(text):
    try:
        gen = pipeline(
            text=text,
            voice=VOICE
        )

        for _, _, audio in gen:
            if state.state.stop_speaking:
                sd.stop()
                break

            sd.play(audio, 24000)
            sd.wait()

    except Exception as e:
        print("[TTS ERROR]", e)

    finally:
        state.state.speaking = False
        state.state.stop_speaking = False


def speak(text):
    if not text:
        return

    if state.state.speaking:
        return

    state.state.speaking = True

    threading.Thread(
        target=_play,
        args=(text,),
        daemon=True
    ).start()

