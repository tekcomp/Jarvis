import numpy as np
import whisper

model = whisper.load_model("medium")

def transcribe(audio):

    import numpy as np

    if isinstance(audio, str):
        return audio  # prevent crash

    if audio is None or len(audio) < 1000:
        return ""

    audio = audio.astype(np.float32) / 32768.0

    result = model.transcribe(audio)

    return result.get("text", "").strip().lower()