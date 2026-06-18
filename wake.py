import webrtcvad
import numpy as np

vad = webrtcvad.Vad(2)

def is_speech(frame_bytes, sample_rate=16000):
    return vad.is_speech(frame_bytes, sample_rate)


def detect_wake(text):
    text = text.lower()
    return "jarvis" in text or "hey jarvis" in text