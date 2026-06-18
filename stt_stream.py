from faster_whisper import WhisperModel
import numpy as np
import wave
import tempfile
import os

model = WhisperModel("base", device="cpu", compute_type="int8")


def transcribe_audio_buffer(audio_buffer):
    if len(audio_buffer) == 0:
        return ""

    audio = np.concatenate(audio_buffer, axis=0)

    tmp_path = os.path.join(tempfile.gettempdir(), "jarvis_audio.wav")

    # write wav safely
    with wave.open(tmp_path, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(16000)
        wf.writeframes((audio * 32767).astype("int16").tobytes())

    # whisper transcription
    segments, _ = model.transcribe(tmp_path)

    text = " ".join([s.text for s in segments]).strip().lower()

    try:
        os.remove(tmp_path)
    except:
        pass

    return text