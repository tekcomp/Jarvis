import webrtcvad
import collections
import pyaudio
import numpy as np

RATE = 16000
FRAME_MS = 30
FRAME_SIZE = int(RATE * FRAME_MS / 1000)

vad = webrtcvad.Vad(2)
pa = pyaudio.PyAudio()


def pick_device():
    for i in range(pa.get_device_count()):
        info = pa.get_device_info_by_index(i)
        if info.get("maxInputChannels", 0) > 0:
            return i
    return None


DEVICE_INDEX = pick_device()

print("MIC DEVICE:", DEVICE_INDEX)

stream = pa.open(
    format=pyaudio.paInt16,
    channels=1,
    rate=RATE,
    input=True,
    input_device_index=DEVICE_INDEX,
    frames_per_buffer=FRAME_SIZE
)

print("✔ VAD READY")


def get_speech_frames():
    ring = collections.deque(maxlen=10)
    voiced = []
    triggered = False

    while True:
        frame = stream.read(FRAME_SIZE, exception_on_overflow=False)

        if len(frame) != FRAME_SIZE * 2:
            continue

        try:
            speech = vad.is_speech(frame, RATE)
        except:
            continue

        if speech:
            voiced.append(frame)
            triggered = True
            ring.clear()

        elif triggered:
            ring.append(frame)

            if len(ring) >= 8:
                if len(voiced) > 5:
                    audio = np.frombuffer(b"".join(voiced), dtype=np.int16)
                    yield audio

                voiced = []
                triggered = False
                ring.clear()