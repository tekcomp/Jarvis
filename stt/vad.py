import webrtcvad
import collections
import pyaudio
import numpy as np

from core.audio_state import audio_state
from core.logger import L3, L5, LOG_LEVEL

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

stream = pa.open(
    format=pyaudio.paInt16,
    channels=1,
    rate=RATE,
    input=True,
    input_device_index=DEVICE_INDEX,
    frames_per_buffer=FRAME_SIZE
)

MAX_SILENCE = 12
MIN_SPEECH = 6


def get_speech_frames():

    L3("VAD LOOP START")

    ring = collections.deque(maxlen=MAX_SILENCE)
    voiced = []
    triggered = False

    while True:

        # 🔥 HARD ECHO BLOCK
        if audio_state.is_blocked():
            continue

        frame_bytes = stream.read(FRAME_SIZE, exception_on_overflow=False)

        if len(frame_bytes) != FRAME_SIZE * 2:
            continue

        try:
            is_speech = vad.is_speech(frame_bytes, RATE)
        except:
            continue

        if LOG_LEVEL >= 5:
            L5(f"VAD speech={is_speech}")

        if is_speech:
            if not triggered:
                L3("SPEECH START")
                triggered = True

            voiced.append(frame_bytes)
            ring.clear()

        else:
            if triggered:
                ring.append(frame_bytes)

                if len(ring) >= MAX_SILENCE:

                    if len(voiced) >= MIN_SPEECH:
                        L3(f"SPEECH END frames={len(voiced)}")
                        print("[VAD] YIELDING AUDIO")
                        audio = np.frombuffer(b"".join(voiced), dtype=np.int16)
                        print("[VAD] YIELDING AUDIO")
                        yield audio

                    voiced = []
                    triggered = False
                    ring.clear()