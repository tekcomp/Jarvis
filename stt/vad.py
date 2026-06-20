import webrtcvad
import collections
import pyaudio
import numpy as np

RATE = 16000          # FIXED for whisper + vad stability
FRAME_MS = 30         # MUST stay 10/20/30 only
FRAME_SIZE = int(RATE * FRAME_MS / 1000)

vad = webrtcvad.Vad(2)

pa = pyaudio.PyAudio()

# safer mic selection (auto fallback)
def pick_device():
    for i in range(pa.get_device_count()):
        info = pa.get_device_info_by_index(i)
        if info.get("maxInputChannels", 0) > 0:
            return i, int(info["defaultSampleRate"])
    return None, 16000


DEVICE_INDEX, DEVICE_RATE = pick_device()

print(f"MIC DEVICE INDEX: {DEVICE_INDEX}")
print(f"DEVICE RATE: {DEVICE_RATE}")

# force safe sample rate
RATE = 16000
CHANNELS = 1

stream = pa.open(
    format=pyaudio.paInt16,
    channels=CHANNELS,
    rate=RATE,
    input=True,
    input_device_index=DEVICE_INDEX,
    frames_per_buffer=FRAME_SIZE
)

print("✔ VAD STREAM READY")


MAX_SILENCE = 12
MIN_SPEECH = 6


def get_speech_frames():
    ring = collections.deque(maxlen=MAX_SILENCE)
    voiced = []
    triggered = False

    while True:
        try:
            frame = stream.read(FRAME_SIZE, exception_on_overflow=False)

            # MUST be exact length
            if len(frame) != FRAME_SIZE * 2:
                continue

            try:
                is_speech = vad.is_speech(frame, RATE)
            except Exception:
                # 🔥 NEVER CRASH PIPELINE
                continue

            if is_speech:
                voiced.append(frame)
                triggered = True
                ring.clear()

            elif triggered:
                ring.append(frame)

                if len(ring) >= MAX_SILENCE:
                    if len(voiced) >= MIN_SPEECH:
                        audio = np.frombuffer(b"".join(voiced), dtype=np.int16)
                        yield audio

                    voiced = []
                    triggered = False
                    ring.clear()

        except Exception as e:
            print("VAD ERROR:", e)
            continue