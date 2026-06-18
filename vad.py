import webrtcvad
import numpy as np

vad = webrtcvad.Vad(2)

def is_speech(frame, sample_rate=16000):
    # frame must be int16 bytes
    return vad.is_speech(frame, sample_rate)