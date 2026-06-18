import sounddevice as sd
import numpy as np
import queue

q = queue.Queue()

SAMPLE_RATE = 16000

def callback(indata, frames, time, status):
    q.put(indata.copy())

def start_stream():
    stream = sd.InputStream(
        samplerate=SAMPLE_RATE,
        channels=1,
        callback=callback,
        blocksize=1024
    )
    stream.start()
    return stream, q