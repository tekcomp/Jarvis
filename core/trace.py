import webrtcvad
import collections
import pyaudio
import numpy as np
import time

# ----------------------------
# CONFIG
# ----------------------------
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

print(f"[VAD] MIC READY (device={DEVICE_INDEX})")

stream = pa.open(
    format=pyaudio.paInt16,
    channels=1,
    rate=RATE,
    input=True,
    input_device_index=DEVICE_INDEX,
    frames_per_buffer=FRAME_SIZE
)

print("[VAD] STREAM READY")

# ----------------------------
# HARD STABILITY SETTINGS
# ----------------------------
MIN_START_SPEECH = 3        # must detect speech for 3 frames before trigger
MAX_SILENCE = 15            # wait longer before closing segment
MIN_TOTAL_FRAMES = 14       # reject short speech

RMS_THRESHOLD = 55

# ----------------------------
# STATE
# ----------------------------
def rms(frame):
    x = np.frombuffer(frame, dtype=np.int16)
    if len(x) == 0:
        return 0
    return float(np.sqrt(np.mean(x.astype(np.float32) ** 2)))


def get_speech_frames():

    voiced = []
    silence_buffer = 0
    speech_buffer = 0
    triggered = False

    while True:
        try:
            frame = stream.read(FRAME_SIZE, exception_on_overflow=False)

            if len(frame) != FRAME_SIZE * 2:
                continue

            is_speech = False
            try:
                is_speech = vad.is_speech(frame, RATE)
            except:
                continue

            energy = rms(frame)

            # ----------------------------
            # START CONDITION (STABILITY GATE)
            # ----------------------------
            if is_speech and energy > RMS_THRESHOLD:
                speech_buffer += 1
            else:
                speech_buffer = 0

            if not triggered and speech_buffer >= MIN_START_SPEECH:
                triggered = True
                voiced = []
                silence_buffer = 0

            # ----------------------------
            # COLLECT AUDIO
            # ----------------------------
            if triggered:
                voiced.append(frame)

                if is_speech:
                    silence_buffer = 0
                else:
                    silence_buffer += 1

                # ----------------------------
                # END SPEECH
                # ----------------------------
                if silence_buffer >= MAX_SILENCE:

                    if len(voiced) >= MIN_TOTAL_FRAMES:

                        full = b"".join(voiced)
                        full_rms = rms(full)

                        # FINAL QUALITY CHECK
                        if full_rms > RMS_THRESHOLD:
                            audio = np.frombuffer(full, dtype=np.int16)
                            yield audio

                    # reset
                    voiced = []
                    triggered = False
                    speech_buffer = 0
                    silence_buffer = 0

        except Exception as e:
            print("[VAD ERROR]", e)
            continue