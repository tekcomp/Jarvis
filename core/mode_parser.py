def detect_mode(text: str):

    t = text.lower()

    # --------------------------
    # PLAYFUL MODE
    # --------------------------
    if "playful" in t:
        return "playful"

    if "fun mode" in t:
        return "playful"

    if "switch to play" in t:
        return "playful"

    # --------------------------
    # JARVIS MODE
    # --------------------------
    if "jarvis" in t:
        return "jarvis"

    # --------------------------
    # ASSISTANT MODE
    # --------------------------
    if "assistant" in t:
        return "assistant"

    if "help mode" in t:
        return "assistant"

    return None