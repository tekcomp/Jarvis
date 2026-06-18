import sounddevice as sd
import numpy as np
import state
import threading

def listener():
    def callback(indata, frames, time, status):
        volume = np.abs(indata).mean()

        if volume > 0.02 and state.state.speaking:
            state.state.stop_speaking = True

    with sd.InputStream(callback=callback, channels=1, samplerate=16000):
        while True:
            sd.sleep(200)


def start():
    threading.Thread(target=listener, daemon=True).start()