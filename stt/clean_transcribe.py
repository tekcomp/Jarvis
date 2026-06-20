import whisper
import numpy as np

model = whisper.load_model("base")  # IMPORTANT: medium is too noisy for real-time


def transcribe(audio: np.ndarray) -> str:

    if audio is None or len(audio) < 2000:
        return ""

    audio = audio.astype(np.float32) / 32768.0

    result = model.transcribe(
        audio,
        fp16=False,
        temperature=0.0,
        condition_on_previous_text=False,   # 🔥 CRITICAL FIX
        beam_size=1,                        # 🔥 reduces hallucinations
        best_of=1,
        language="en"
    )

    text = result.get("text", "").strip().lower()

    # -----------------------------
    # HARD FILTER (VERY IMPORTANT)
    # -----------------------------
    junk_phrases = [
        "thanks for watching",
        "bye",
        "subscribe",
        "music",
        "applause"
    ]

    for j in junk_phrases:
        if j in text:
            return ""

    return text