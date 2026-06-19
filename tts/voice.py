import sounddevice as sd
from kokoro import KPipeline
import threading
import state

pipeline = KPipeline(lang_code="a", device="cpu")

# ✅ SAFE VOICE (verified working fallback)
VOICE = "af_heart"


def _play(text: str):
    if not text:
        return

    if state.state.stop_speaking:
        return

    try:
        gen = pipeline(text=text, voice=VOICE)

        for _, _, audio in gen:
            if state.state.stop_speaking:
                sd.stop()
                return

            sd.play(audio, 24000)
            sd.wait()

    except Exception as e:
        print("[TTS ERROR]", e)


def speak_stream(text: str):
    if not text:
        return

    state.state.speaking = True
    state.state.stop_speaking = False

    threading.Thread(target=_play, args=(text,), daemon=True).start()


# BACKWARD COMPAT
def speak(text: str):
    return speak_stream(text)