import numpy as np
import whisper

from core.logger import L3, L5, LOG_LEVEL

model = whisper.load_model("medium")


def transcribe(audio):

    if isinstance(audio, str):
        return ""

    if audio is None or len(audio) < 1000:
        return ""

    audio = audio.astype(np.float32) / 32768.0

    result = model.transcribe(audio)
    text = result.get("text", "").strip().lower()

    if not text:
        L3("WHISPER EMPTY RESULT")
        return ""

    # debug logging (only when enabled)
    if LOG_LEVEL >= 5:
        L5(f"WHISPER RAW: {text}")

    return text