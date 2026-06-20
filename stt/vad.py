import webrtcvad
import collections
import pyaudio
import numpy as np
import time
import state

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

print(f"✔ MIC DEVICE: {DEVICE_INDEX}")
print("✔ VAD READY (CLEAN CUT V17.1)")


stream = pa.open(
    format=pyaudio.paInt16,
    channels=1,
    rate=RATE,
    input=True,
    input_device_index=DEVICE_INDEX,
    frames_per_buffer=FRAME_SIZE
)


# -------------------------
# CRITICAL FIX PARAMETERS
# -------------------------
PRE_ROLL = 5            # smaller buffer = less bleed-in
END_SILENCE = 10        # faster cutoff (IMPORTANT FIX)
MIN_AUDIO = 12


def get_speech_frames():

    ring = collections.deque(maxlen=PRE_ROLL)
    voiced = []
    silence_count = 0
    triggered = False

    print("LISTENING...")

    while True:

        try:

            if state.state.ignore_audio:
                time.sleep(0.01)
                continue

            frame = stream.read(FRAME_SIZE, exception_on_overflow=False)

            if len(frame) != FRAME_SIZE * 2:
                continue

            speech = vad.is_speech(frame, RATE)

            if speech:

                if not triggered:
                    voiced.extend(list(ring))  # pre-roll capture
                    triggered = True

                voiced.append(frame)
                silence_count = 0
                ring.append(frame)

            else:

                if triggered:
                    silence_count += 1

                    # append only very small tail (CRITICAL FIX)
                    if silence_count < END_SILENCE:
                        voiced.append(frame)

                    if silence_count >= END_SILENCE:

                        if len(voiced) >= MIN_AUDIO:

                            # 🔥 TRIM LAST 200ms (removes Whisper garbage tail)
                            trim_frames = int(0.2 * RATE / FRAME_SIZE)
                            cleaned = voiced[:-trim_frames] if len(voiced) > trim_frames else voiced

                            audio = np.frombuffer(b"".join(cleaned), dtype=np.int16)
                            yield audio

                        # reset
                        voiced = []
                        silence_count = 0
                        triggered = False
                        ring.clear()

                else:
                    ring.append(frame)

        except Exception as e:
            print("VAD ERROR:", e)
            time.sleep(0.1)