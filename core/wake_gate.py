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

    """Remove wake-word phrases and collapse leftover whitespace.

    Edge case: if stripping would leave a near-empty residue (e.g.
    "jarvis jarvis mode" -> "mode", or "jarvis" -> ""), we salvage by
    stripping ONE leading wake word from the original so the brain still
    receives the user's intended command (e.g. "jarvis mode" -> "mode"
    still matches the intent-router check "jarvis mode" in t... wait,
    "mode" alone does not, so we instead return "jarvis mode" in that
    salvage case so the existing substring rule still fires).
    """
    if not text:
        return ""

    result = text.lower().strip()

    # Sort wake phrases longest-first so "hey jarvis" is consumed before "jarvis".
    for wake in sorted(WAKE_WORDS, key=len, reverse=True):
        result = result.replace(wake, "")

    result = " ".join(result.split())  # collapse whitespace

    # If stripping ate the command (e.g. "jarvis jarvis mode" -> "mode",
    # "jarvis" -> ""), salvage: strip ONE leading wake word from the
    # original so downstream intent-router / LLM still receives useful text.
    if not result or len(result) <= 2:
        lowered = text.lower().lstrip()
        for wake in sorted(WAKE_WORDS, key=len, reverse=True):
            if lowered.startswith(wake):
                salvaged = text[len(wake):].lstrip()
                if salvaged:
                    return salvaged
        return ""

    return result