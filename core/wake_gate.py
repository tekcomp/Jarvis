# =========================================================
# core/wake_gate.py
# =========================================================

WAKE_WORDS = [
    "jarvis",
    "hey jarvis",
    "okay jarvis",
    "ok jarvis"
]


def contains_wake_word(text: str) -> bool:

    if not text:
        return False

    text = text.lower().strip()

    return any(word in text for word in WAKE_WORDS)


def strip_wake_word(text: str) -> str:

    if not text:
        return ""

    result = text.lower().strip()

    for wake in WAKE_WORDS:
        result = result.replace(wake, "")

    return result.strip()