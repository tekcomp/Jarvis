from datetime import datetime

WAKE_WORD = "jarvis"
active = False


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

    if "bye" in text or "goodbye" in text:
        return "Going idle."

    return "I didn't understand that clearly."


def handle(text: str) -> str:

    global active

    if not text:
        return ""

    raw = text.lower().strip()

    # -------------------------
    # WAKE WORD MODE
    # -------------------------
    if WAKE_WORD in raw:
        active = True

        cleaned = raw.replace(WAKE_WORD, "").strip(",. ")

        if cleaned:
            return _process(cleaned)

        return "Yes?"

    # -------------------------
    # IMPORTANT FIX: ALWAYS ALLOW COMMANDS
    # -------------------------
    if active:
        return _process(raw)

    # -------------------------
    # PASSIVE MODE (CRITICAL FIX)
    # -------------------------
    # allow basic commands even without wake word
    if any(x in raw for x in ["time", "date", "joke", "weather"]):
        return _process(raw)

    return ""