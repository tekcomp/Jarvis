import numpy as np
import whisper

from core.logger import L3, LOG_LEVEL
from core.duplex_guard import duplex

model = whisper.load_model("medium")


def transcribe(audio):

    # 🔥 ignore TTS echo window
    if duplex.muted():
        return ""

    if audio is None or len(audio) < 1000:
        return ""

    audio = audio.astype(np.float32) / 32768.0

    result = model.transcribe(audio)
    text = result.get("text", "").strip().lower()

    if not text:
        L3("WHISPER EMPTY RESULT")
        return ""

    if LOG_LEVEL >= 3:
        L3(f"WHISPER: {text}")

    return text