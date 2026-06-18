import sounddevice as sd
import numpy as np
import queue

SAMPLE_RATE = 16000
BLOCK_SIZE = 1024

audio_queue = queue.Queue()

def callback(indata, frames, time, status):
    audio_queue.put(indata.copy())

def start_stream():
    stream = sd.InputStream(
        samplerate=SAMPLE_RATE,
        channels=1,
        dtype="float32",
        blocksize=BLOCK_SIZE,
        callback=callback
    )
    stream.start()
    return stream, audio_queue