import sounddevice as sd
from kokoro import KPipeline
import state

pipeline = KPipeline(lang_code="a", device="cpu")
VOICE = "af_heart"


def speak(text):
    state.speaking = True
    state.stop_speaking = False

    print("Jarvis:", text)

    generator = pipeline(text=text, voice=VOICE)

    for _, _, audio in generator:

        # 🔥 BARGE-IN SUPPORT
        if state.stop_speaking:
            sd.stop()
            break

        sd.play(audio, 24000)
        sd.wait()

    state.speaking = False