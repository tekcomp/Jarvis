# core/intent_gate.py

import re

# -----------------------------
# CONFIG
# -----------------------------
MIN_LENGTH = 4
MIN_INTENT_SCORE = 0.55

NOISE_PHRASES = {
    "thanks for watching",
    "thank you for watching",
    "uh",
    "hmm",
    "okay",
    "bye",
    "service",
    "drivers",
    "hello hello",
    "undefined",
}

COMMAND_KEYWORDS = {
    "jarvis": 1.0,
    "hey": 0.6,
    "what": 0.4,
    "tell": 0.4,
    "joke": 0.8,
    "time": 0.9,
    "date": 0.9,
    "weather": 0.9,
    "capital": 0.9,
}


# -----------------------------
# CLEAN TEXT
# -----------------------------
def clean(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^\w\s]", "", text)
    return text


# -----------------------------
# INTENT SCORING
# -----------------------------
def intent_score(text: str) -> float:
    score = 0.0
    words = text.split()

    if not words:
        return 0.0

    # keyword scoring
    for w in words:
        if w in COMMAND_KEYWORDS:
            score += COMMAND_KEYWORDS[w]

    # normalize by length
    score = score / max(1, len(words))

    # boost if contains command verbs
    if any(w in text for w in ["what", "tell", "give", "show", "is", "are"]):
        score += 0.2

    return min(score, 1.0)


# -----------------------------
# VALIDITY CHECK
# -----------------------------
def is_valid(text: str) -> bool:
    if not text:
        return False

    text = clean(text)

    if len(text) < MIN_LENGTH:
        return False

    if text in NOISE_PHRASES:
        return False

    return True


# -----------------------------
# MAIN GATE FUNCTION
# -----------------------------
def should_process(text: str) -> bool:
    text = clean(text)

    if not is_valid(text):
        return False

    score = intent_score(text)

    return score >= MIN_INTENT_SCORE


def debug_score(text: str):
    text = clean(text)
    return {
        "text": text,
        "intent_score": intent_score(text),
        "valid": is_valid(text),
        "pass": should_process(text),
    }