from datetime import datetime
from core.memory import add, get_context

WAKE_WORD = "jarvis"

active = False


# =========================================================
# CORE PROCESSOR
# =========================================================
def _process(text: str) -> str:

    text = text.strip()

    # store user input in memory
    add("user", text)

    response = ""

    # -------------------------
    # INTENT ROUTING
    # -------------------------
    if "time" in text:
        response = f"The time is {datetime.now().strftime('%H:%M')}."

    elif "date" in text:
        response = f"Today is {datetime.now().strftime('%A %B %d')}."

    elif "joke" in text:
        response = "Why did the AI cross the road? To optimize the reward function."

    elif "weather" in text:
        response = "Weather module not connected yet."

    elif any(x in text for x in ["bye", "goodbye", "stop listening"]):
        response = "Going idle."

    else:
        response = "I didn't understand that clearly."

    # store assistant response in memory
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

    # =====================================================
    # WAKE WORD DETECTION
    # =====================================================
    if WAKE_WORD in raw:

        active = True

        cleaned = raw.replace(WAKE_WORD, "").strip(",. ")

        # wake only
        if cleaned == "":
            response = "Yes?"
            add("assistant", response)
            return response

        return _process(cleaned)

    # =====================================================
    # ACTIVE MODE (CONVERSATION STATE)
    # =====================================================
    if active:
        return _process(raw)

    # =====================================================
    # PASSIVE MODE (LIGHT FILTER ONLY)
    # =====================================================
    # allow only simple direct commands
    if any(x in raw for x in ["time", "date", "joke", "weather"]):
        return _process(raw)

    # ignore everything else
    return ""