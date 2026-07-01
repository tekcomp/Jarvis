import sounddevice as sd
import numpy as np
import queue

q = queue.Queue()

SAMPLE_RATE = 16000

# Pin the input device by name so we don't follow Windows default changes.
# Fall back to system default if the named device isn't present.
_PREFERRED_MIC_NAME = "USB Audio Device"


def _resolve_mic_device() -> int | None:
    try:
        for i, dev in enumerate(sd.query_devices()):
            if _PREFERRED_MIC_NAME.lower() in dev["name"].lower() and dev["max_input_channels"] > 0:
                return i
    except Exception:
        pass
    return None


def callback(indata, frames, time, status):
    q.put(indata.copy())


def start_stream():
    mic_device = _resolve_mic_device()
    stream_kwargs = dict(
        samplerate=SAMPLE_RATE,
        channels=1,
        callback=callback,
        blocksize=1024,
    )
    if mic_device is not None:
        stream_kwargs["device"] = mic_device
    stream = sd.InputStream(**stream_kwargs)
    stream.start()
    return stream, q