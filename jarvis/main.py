import sounddevice as sd
import numpy as np
import queue

from core.brain import handle
from audio.interrupt import start as start_interrupt


# -------------------------
# AUDIO QUEUE (mic stream)
# -------------------------
audio_queue = queue.Queue()


def callback(indata, frames, time, status):
    audio_queue.put(indata.copy())


def main():
    print("Jarvis ONLINE (Voice Mode)")

    # 🔥 Start interrupt listener (barge-in system)
    start_interrupt()

    # Microphone stream
    stream = sd.InputStream(
        samplerate=16000,
        channels=1,
        dtype="float32",
        callback=callback
    )

    buffer = []
    silence_counter = 0

    with stream:
        while True:
            audio = audio_queue.get().flatten()

            volume = np.abs(audio).mean()

            # -------------------------
            # SPEECH DETECTION
            # -------------------------
            if volume > 0.01:
                buffer.append(audio)
                silence_counter = 0
            else:
                silence_counter += 1

            # -------------------------
            # END OF SPEECH CHUNK
            # -------------------------
            if silence_counter > 20 and len(buffer) > 10:
                handle(buffer)
                buffer = []


if __name__ == "__main__":
    main()