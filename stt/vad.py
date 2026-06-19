import webrtcvad
import collections
import pyaudio
import numpy as np

RATE = 16000
FRAME_MS = 30
FRAME_SIZE = int(RATE * FRAME_MS / 1000)

vad = webrtcvad.Vad(2)

audio = pyaudio.PyAudio()

stream = audio.open(
    format=pyaudio.paInt16,
    channels=1,
    rate=RATE,
    input=True,
    frames_per_buffer=FRAME_SIZE
)

# -----------------------------
# FILTER SETTINGS (IMPORTANT)
# -----------------------------
MAX_SILENCE_FRAMES = 10
MIN_SPEECH_FRAMES = 5
NOISE_FILTER_MIN_LEN = 3


def get_speech_frames():
    ring = collections.deque(maxlen=MAX_SILENCE_FRAMES)

    voiced = []
    triggered = False

    while True:
        frame = stream.read(FRAME_SIZE, exception_on_overflow=False)

        if len(frame) != FRAME_SIZE * 2:
            continue

        is_speech = vad.is_speech(frame, RATE)

        if is_speech:
            voiced.append(frame)
            triggered = True
            ring.clear()

        elif triggered:
            ring.append(frame)

            # end of speech detected
            if len(ring) >= MAX_SILENCE_FRAMES:

                if len(voiced) >= MIN_SPEECH_FRAMES:

                    audio_data = np.frombuffer(
                        b"".join(voiced),
                        dtype=np.int16
                    )

                    yield audio_data

                # reset
                voiced = []
                triggered = False
                ring.clear()