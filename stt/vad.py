import webrtcvad
import collections
import pyaudio
import numpy as np
import state

# =========================
# SAFE AUDIO CONFIG
# =========================

RATE = 48000  # SAFE for USB headsets on Windows
FRAME_MS = 30

# WebRTC VAD ONLY supports 10/20/30ms frames
FRAME_SIZE = int(RATE * FRAME_MS / 1000)

vad = webrtcvad.Vad(2)

audio = pyaudio.PyAudio()

# =========================
# DEVICE SELECTION (SAFE)
# =========================

def pick_input_device():
    print("\n--- SCANNING INPUT DEVICES ---")

    best_device = None

    for i in range(audio.get_device_count()):
        info = audio.get_device_info_by_index(i)

        name = info.get("name", "")
        in_ch = int(info.get("maxInputChannels", 0))

        if in_ch > 0:
            print(f"[{i}] {name} | IN: {in_ch}")

            # prefer real mic devices
            if best_device is None:
                if "Microphone" in name or "USB" in name:
                    best_device = i

    if best_device is None:
        best_device = audio.get_default_input_device_info()["index"]

    return best_device


DEVICE_INDEX = pick_input_device()
device_info = audio.get_device_info_by_index(DEVICE_INDEX)

print("\nSELECTED DEVICE:", device_info["name"])
print("RATE:", RATE)
print("CHANNELS:", 1)

# =========================
# SAFE STREAM OPEN (FIXED)
# =========================

def open_stream():
    for rate in [48000, 44100, 32000, 16000]:
        try:
            print(f"Trying audio rate: {rate}")

            frame_size = int(rate * FRAME_MS / 1000)

            stream = audio.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=rate,
                input=True,
                input_device_index=DEVICE_INDEX,
                frames_per_buffer=frame_size
            )

            print(f"✔ Stream opened at {rate}")
            return stream, rate, frame_size

        except Exception as e:
            print("✖ Failed rate", rate, "->", e)

    raise RuntimeError("No working audio configuration found")


stream, RATE, FRAME_SIZE = open_stream()

# =========================
# VAD SETTINGS
# =========================

MAX_SILENCE = 12
MIN_SPEECH = 6

# =========================
# MAIN STREAM LOOP
# =========================

def get_speech_frames():
    print("\nVAD ONLINE (STABLE PIPELINE)\n")

    ring = collections.deque(maxlen=MAX_SILENCE)
    voiced = []
    triggered = False

    while True:

        # pause when speaking
        if state.state.speaking:
            continue

        try:
            frame = stream.read(FRAME_SIZE, exception_on_overflow=False)

        except Exception as e:
            print("STREAM ERROR:", e)
            continue

        if len(frame) == 0:
            continue

        # WebRTC VAD requires exact frame sizes
        if len(frame) != FRAME_SIZE * 2:
            continue

        try:
            is_speech = vad.is_speech(frame, RATE)
        except Exception:
            continue

        if is_speech:
            voiced.append(frame)
            triggered = True
            ring.clear()

        elif triggered:
            ring.append(frame)

            if len(ring) >= MAX_SILENCE:

                if len(voiced) >= MIN_SPEECH:

                    audio_data = np.frombuffer(
                        b"".join(voiced),
                        dtype=np.int16
                    )

                    yield audio_data

                voiced = []
                triggered = False
                ring.clear()