import webrtcvad
import collections
import pyaudio
import numpy as np

RATE = 16000
FRAME_MS = 30
FRAME_SIZE = int(RATE * FRAME_MS / 1000)

vad = webrtcvad.Vad(3)  # 🔥 MAX AGGRESSIVENESS (IMPORTANT)

pa = pyaudio.PyAudio()

# ----------------------------
# DEVICE SELECTION
# ----------------------------
def pick_device():
    for i in range(pa.get_device_count()):
        info = pa.get_device_info_by_index(i)
        if info.get("maxInputChannels", 0) > 0:
            return i
    return 0

DEVICE_INDEX = pick_device()


stream = pa.open(
    format=pyaudio.paInt16,
    channels=1,
    rate=RATE,
    input=True,
    input_device_index=DEVICE_INDEX,
    frames_per_buffer=FRAME_SIZE
)

print("✔ VAD READY (NOISE FILTER V18)")


# ----------------------------
# QUALITY FILTER SETTINGS
# ----------------------------
MIN_FRAMES = 8          # must hear real speech burst
MAX_SILENCE = 10        # stop faster (reduce junk tails)
ENERGY_THRESHOLD = 500  # 🔥 key noise filter


def energy(frame):
    audio = np.frombuffer(frame, dtype=np.int16)
    return np.abs(audio).mean()


def get_speech_frames():

    ring = collections.deque(maxlen=MAX_SILENCE)
    voiced = []
    triggered = False

    while True:

        frame = stream.read(FRAME_SIZE, exception_on_overflow=False)

        if len(frame) != FRAME_SIZE * 2:
            continue

        # ----------------------------
        # 🔥 HARD ENERGY FILTER FIRST
        # ----------------------------
        if energy(frame) < ENERGY_THRESHOLD:
            continue

        # ----------------------------
        # VAD CHECK
        # ----------------------------
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

            if len(ring) >= MAX_SILENCE:

                # ----------------------------
                # 🔥 QUALITY GATE BEFORE WHISPER
                # ----------------------------
                if len(voiced) >= MIN_FRAMES:

                    audio = np.frombuffer(
                        b"".join(voiced),
                        dtype=np.int16
                    )

                    yield audio

                voiced = []
                triggered = False
                ring.clear()