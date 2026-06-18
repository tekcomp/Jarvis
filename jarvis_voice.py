import sounddevice as sd
from kokoro import KPipeline
import state
import threading

pipeline = KPipeline(lang_code="a", device="cpu")
VOICE = "af_heart"


def _play_audio_stream(generator):
    state.speaking = True
    state.stop_speaking = False

    for _, _, audio in generator:

        # 🔥 BARGE-IN CHECK (THIS IS THE MAGIC)
        if state.stop_speaking:
            sd.stop()
            break

        sd.play(audio, 24000)
        sd.wait()

    state.speaking = False


def speak(text):
    print("Jarvis:", text)

    gen = pipeline(text=text, voice=VOICE)

    thread = threading.Thread(target=_play_audio_stream, args=(gen,))
    thread.start()