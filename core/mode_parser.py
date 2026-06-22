# core/mode_parser.py (NEW FILE OR INLINE)

import re

def detect_mode(text: str):
    t = text.lower()

    # flexible matching (fixes "travis", "play for", etc.)
    if re.search(r"\b(playful)\b", t):
        return "playful"

    if re.search(r"\b(jarvis)\b", t):
        return "jarvis"

    if re.search(r"\b(assistant)\b", t):
        return "assistant"

    return None