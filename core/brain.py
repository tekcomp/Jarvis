from datetime import datetime

WAKE_WORD = "jarvis"

active = False


def _clean(text: str) -> str:
    """
    Removes wake word + cleans punctuation noise
    """
    text = text.lower().strip()

    # remove wake word cleanly (not just detect it)
    text = text.replace(WAKE_WORD, "")

    # cleanup leftover punctuation/spaces
    return text.replace(",", "").replace(".", "").strip()


def handle(text: str) -> str:

    global active

    if not text:
        return ""

    raw = text.lower().strip()
    cleaned = _clean(raw)

    # -------------------------
    # WAKE WORD GATE
    # -------------------------
    if not active:

        if WAKE_WORD in raw:
            active = True

            # if user ONLY said "jarvis", don't continue processing
            if cleaned == "":
                return "Yes?"

            # if wake word + command in same sentence
            return _process(cleaned)

        return ""   # ignore everything else

    # -------------------------
    # EXIT CONDITIONS
    # -------------------------
    if any(x in cleaned for x in ["sleep", "stop listening", "goodbye"]):
        active = False
        return "Going idle."

    # -------------------------
    # EMPTY SAFETY
    # -------------------------
    if cleaned == "":
        return ""

    # -------------------------
    # NORMAL COMMAND FLOW
    # -------------------------
    return _process(cleaned)


def _process(text: str) -> str:

    text = text.strip()

    if "time" in text:
        return f"The time is {datetime.now().strftime('%H:%M')}."

    if "date" in text:
        return f"Today is {datetime.now().strftime('%A %B %d')}."

    if "joke" in text:
        return "Why did the AI cross the road? To optimize the reward function."

    if "weather" in text:
        return "Weather module not connected yet."
    
    if "goodbye" in text:
        return "Goodbye! Have a great day!"
    

    return "I didn't understand that clearly."