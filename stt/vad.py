import webrtcvad
import collections
import numpy as np
import pyaudio

vad = webrtcvad.Vad(2)

RATE = 16000
FRAME_MS = 30
FRAME_SIZE = int(RATE * FRAME_MS / 1000)

audio = pyaudio.PyAudio()

stream = audio.open(
    format=pyaudio.paInt16,
    channels=1,
    rate=RATE,
    input=True,
    frames_per_buffer=FRAME_SIZE
)

SILENCE_LIMIT = 20  # ~600ms silence


def get_speech_frames():
    voiced_frames = []
    silence_count = 0
    triggered = False

    while True:
        frame = stream.read(FRAME_SIZE, exception_on_overflow=False)

        is_speech = vad.is_speech(frame, RATE)

        if is_speech:
            voiced_frames.append(frame)
            triggered = True
            silence_count = 0

        else:
            if triggered:
                silence_count += 1

                if silence_count > SILENCE_LIMIT:
                    audio_np = np.frombuffer(b"".join(voiced_frames), dtype=np.int16)

                    voiced_frames = []
                    triggered = False
                    silence_count = 0

                    yield audio_np