import time
import sounddevice as sd

from core.logger import L3
from core.duplex_guard import duplex
from tts.engine import synthesize_audio


SAMPLE_RATE = 24000


def speak(text: str):

    if not text:
        return

    L3(f"TTS START: {text}")

    # activate echo suppression window
    duplex.start(hold_seconds=1.8)

    try:
        audio = synthesize_audio(text)

        _play(audio)

    finally:
        duplex.stop()
        L3("TTS END")


def _play(audio):

    # small buffer to prevent immediate re-capture
    time.sleep(0.05)

    sd.play(audio, samplerate=SAMPLE_RATE)
    sd.wait()