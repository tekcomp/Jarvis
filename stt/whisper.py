import whisper
import numpy as np
import tempfile
import wave


model = whisper.load_model("base")  # or "small" for better accuracy


def transcribe(audio_buffer):
    """
    audio_buffer = list of numpy arrays from mic
    """

    audio = np.concatenate(audio_buffer)

    # Save temp wav file
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        with wave.open(f.name, "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(16000)
            wf.writeframes((audio * 32767).astype(np.int16).tobytes())

        result = model.transcribe(f.name)

    return result["text"]