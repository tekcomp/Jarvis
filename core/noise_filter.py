# =========================================================
# core/noise_filter.py
# Noise Rejection Layer (NRL v1)
# =========================================================

HALLUCINATIONS = {
    "thanks for watching",
    "thank you",
    "goodbye",
    "bye",
    "see you next time",
    "music",
    "captions by",
    "subtitles by",
    ".",
    "..",
    "..."
}

MIN_TEXT_LENGTH = 5


def is_valid_transcript(text: str) -> bool:

    if not text:
        return False

    text = text.strip().lower()

    if len(text) < MIN_TEXT_LENGTH:
        return False

    if text in HALLUCINATIONS:
        return False

    return True