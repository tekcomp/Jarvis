import numpy as np
import whisper

model = whisper.load_model("medium")

def transcribe(audio):

    if audio is None:
        return ""

    # If already numpy array from VAD → use directly
    if isinstance(audio, np.ndarray):
        audio_np = audio

    else:
        # fallback safety
        audio_np = np.frombuffer(audio, dtype=np.int16)

    # normalize for Whisper
    audio_np = audio_np.astype("float32") / 32768.0

    result = model.transcribe(audio_np)

    return result["text"].strip()