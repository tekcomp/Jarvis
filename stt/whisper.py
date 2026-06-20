import numpy as np
import whisper
import re

model = whisper.load_model("medium")

NOISE_PHRASES = {
    "thanks for watching",
    "thank you for watching",
    "you",
    "uh",
    "hmm",
    "okay",
    "ok",
    "bye"
}


def normalize(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^\w\s]", "", text)
    return text


def dedupe_words(text: str) -> str:
    words = text.split()
    if len(words) < 2:
        return text

    cleaned = [words[0]]
    for w in words[1:]:
        if w != cleaned[-1]:
            cleaned.append(w)

    return " ".join(cleaned)


def transcribe(audio):

    if isinstance(audio, str):
        return ""

    if audio is None or len(audio) < 1200:
        return ""

    audio = audio.astype(np.float32) / 32768.0

    result = model.transcribe(audio)

    text = result.get("text", "")
    text = normalize(text)

    if text in NOISE_PHRASES:
        return ""

    text = dedupe_words(text)

    return text