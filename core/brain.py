from datetime import datetime
from core.memory import add

WAKE_WORD = "jarvis"
active = False


# =========================================================
# RESET (CI SAFE)
# =========================================================
def reset():
    global active
    active = False


# =========================================================
# CORE PROCESSOR
# =========================================================
def _process(text: str) -> str:

    text = text.strip().lower()

    # stricter noise filter
    if not text or len(text.split()) < 2:
        return ""

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
    elif "date" in text:
        response = f"Today is {datetime.now().strftime('%A %B %d')}."

    elif "today" in text and "date" in text:
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
    # DEMO
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
    elif "bye" in text or "goodbye" in text or "stop listening" in text:
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
    # WAKE WORD MODE
    # -----------------------------------------------------
    if WAKE_WORD in raw:

        active = True
        cleaned = raw.replace(WAKE_WORD, "").strip(",. ")

        if not cleaned:
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
    # PASSIVE MODE (STRICT FILTER)
    # -----------------------------------------------------
    passive_triggers = ("time", "date", "today", "joke", "weather", "demo")

    if any(t in raw for t in passive_triggers):
        return _process(raw)

    return ""