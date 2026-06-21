from datetime import datetime
from core.memory import add

WAKE_WORD = "jarvis"

active = False


def reset():
    global active
    active = False


# =========================================================
# CORE PROCESSOR
# =========================================================
def _process(text: str) -> str:

    text = text.strip().lower()

    add("user", text)

    response = ""

    # -----------------------------------------------------
    # TIME
    # -----------------------------------------------------
    if "time" in text:
        response = f"The time is {datetime.now().strftime('%H:%M')}."

    # -----------------------------------------------------
    # DATE
    # -----------------------------------------------------
    elif "date" in text or "today" in text:
        response = f"Today is {datetime.now().strftime('%A %B %d')}."

    # -----------------------------------------------------
    # JOKE
    # -----------------------------------------------------
    elif "joke" in text:
        response = (
            "Why did the AI cross the road? "
            "To optimize the reward function."
        )

    # -----------------------------------------------------
    # WEATHER
    # -----------------------------------------------------
    elif "weather" in text:
        response = "Weather module not connected yet."

    # -----------------------------------------------------
    # DEMO COMMANDS
    # -----------------------------------------------------
    elif "what can you do" in text:
        response = (
            "I can tell the time, date, jokes, "
            "and maintain conversation state."
        )

    elif "demo" in text or "show features" in text:
        response = (
            "I am Jarvis. I support wake words, "
            "speech recognition, memory, "
            "and real-time voice responses."
        )

    # -----------------------------------------------------
    # EXIT
    # -----------------------------------------------------
    elif any(x in text for x in ["bye", "goodbye", "stop listening"]):
        global active
        active = False
        response = "Going idle."

    # -----------------------------------------------------
    # UNKNOWN
    # -----------------------------------------------------
    else:
        response = "I didn't understand that clearly."

    add("assistant", response)

    return response


# =========================================================
# ENTRY POINT
# =========================================================
def handle(text: str) -> str:

    global active

    if not text:
        return ""

    raw = text.lower().strip()

    # -----------------------------------------------------
    # WAKE WORD
    # -----------------------------------------------------
    if WAKE_WORD in raw:

        active = True

        cleaned = raw.replace(WAKE_WORD, "").strip(",. ")

        if cleaned == "":
            response = "Yes?"
            add("assistant", response)
            return response

        return _process(cleaned)

    # -----------------------------------------------------
    # ACTIVE MODE
    # -----------------------------------------------------
    if active:
        return _process(raw)

    # -----------------------------------------------------
    # PASSIVE COMMANDS
    # -----------------------------------------------------
    if any(
        x in raw
        for x in [
            "time",
            "date",
            "today",
            "joke",
            "weather",
            "demo",
        ]
    ):
        return _process(raw)

    return ""