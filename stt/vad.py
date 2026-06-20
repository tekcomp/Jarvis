import webrtcvad
import collections
import pyaudio
import numpy as np
import threading

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

print("✔ VAD READY (V11 SAFE)")


# -----------------------------
# CONTROL FLAG (CLEAN STOP)
# -----------------------------
_running = True


def stop_vad():
    global _running
    _running = False


# -----------------------------
# MAIN LOOP
# -----------------------------
def get_speech_frames():

    global _running

    ring = collections.deque(maxlen=20)
    voiced = []
    triggered = False

    try:
        while _running:

            try:
                frame = stream.read(FRAME_SIZE, exception_on_overflow=False)
            except Exception:
                continue

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

                if len(ring) >= 15:

                    if len(voiced) > 8:

                        audio = np.frombuffer(
                            b"".join(voiced),
                            dtype=np.int16
                        )

                        yield audio

                    voiced = []
                    triggered = False
                    ring.clear()

    except KeyboardInterrupt:
        print("\n🛑 VAD STOPPED CLEANLY")
        stop_vad()
        return

    finally:
        try:
            stream.stop_stream()
            stream.close()
        except:
            pass
        pa.terminate()