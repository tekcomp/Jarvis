import time
import threading
import sounddevice as sd

from core.logger import L3
from .engine import synthesize_audio

_is_speaking = False
_lock = threading.Lock()


def is_speaking():
    return _is_speaking


def speak(text: str):
    global _is_speaking

    if not text:
        return

    with _lock:
        _is_speaking = True

    try:
        L3(f"TTS START: {text}")

        audio = synthesize_audio(text)

        _play(audio)

    finally:
        with _lock:
            _is_speaking = False

        L3("TTS END")


def _play(audio):
    global _is_speaking

    try:
        with _lock:
            _is_speaking = True

        # hard stop any overlapping audio
        sd.stop()

        # play audio (blocking = stable for VAD systems)
        sd.play(audio, samplerate=24000)
        sd.wait()

    finally:
        with _lock:
            _is_speaking = False