import sounddevice as sd
import numpy as np
import queue

from core.brain import handle
from audio.interrupt import start as start_interrupt

q = queue.Queue()


def callback(indata, frames, time, status):
    q.put(indata.copy())


def main():
    print("Jarvis ONLINE")

    # 🔥 START INTERRUPT ENGINE
    start_interrupt()

    stream = sd.InputStream(
        samplerate=16000,
        channels=1,
        callback=callback
    )

    buffer = []
    silence = 0

    with stream:
        while True:
            audio = q.get().flatten()
            volume = np.abs(audio).mean()

            if volume > 0.01:
                buffer.append(audio)
                silence = 0
            else:
                silence += 1

            if silence > 20 and buffer:
                handle(buffer)
                buffer = []


if __name__ == "__main__":
    main()