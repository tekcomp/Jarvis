import webrtcvad
import collections
import pyaudio
import numpy as np
import time

RATE = 16000
FRAME_MS = 30
FRAME_SIZE = int(RATE * FRAME_MS / 1000)

vad = webrtcvad.Vad(2)

pa = pyaudio.PyAudio()

# -----------------------------
# PICK DEVICE SAFELY
# -----------------------------
def pick_device():
    for i in range(pa.get_device_count()):
        info = pa.get_device_info_by_index(i)
        if info.get("maxInputChannels", 0) > 0:
            return i
    return 0


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


# -----------------------------
# STABILITY SETTINGS (KEY FIX)
# -----------------------------
SILENCE_LIMIT = 25          # increased stability
MIN_SPEECH = 8
HOLD_FRAMES = 5             # extra smoothing


def get_speech_frames():

    ring = collections.deque(maxlen=SILENCE_LIMIT)

    voiced = []
    triggered = False

    last_voice_time = 0

    while True:

        frame = stream.read(FRAME_SIZE, exception_on_overflow=False)

        if len(frame) != FRAME_SIZE * 2:
            continue

        try:
            is_speech = vad.is_speech(frame, RATE)
        except:
            continue

        # -----------------------------
        # SPEECH DETECTED
        # -----------------------------
        if is_speech:
            voiced.append(frame)
            triggered = True
            last_voice_time = time.time()
            ring.clear()

        # -----------------------------
        # SILENCE DETECTED
        # -----------------------------
        elif triggered:
            ring.append(frame)

            silence_duration = len(ring)

            # WAIT LONGER BEFORE FINALIZING
            if silence_duration >= SILENCE_LIMIT:

                # VALID SPEECH CHECK
                if len(voiced) >= MIN_SPEECH:

                    audio = np.frombuffer(
                        b"".join(voiced),
                        dtype=np.int16
                    )

                    yield audio

                # RESET CLEANLY
                voiced = []
                triggered = False
                ring.clear()