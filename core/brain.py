from datetime import datetime
from core.memory import add

WAKE_WORD = "jarvis"

active = False


# =========================================================
# RESET (USED BY CI ONLY)
# =========================================================
def reset():
    global active
    active = False


# =========================================================
# CORE PROCESSOR
# =========================================================
def _process(text: str) -> str:

    text = text.strip()

    add("user", text)

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

    add("assistant", response)
    return response


# =========================================================
# ENTRY POINT
# =========================================================
def handle(text: str, reset_mode: bool = False) -> str:
    global active

    if reset_mode:
        active = False

    if not text:
        return ""

    raw = text.lower().strip()

    # -------------------------
    # WAKE WORD
    # -------------------------
    if WAKE_WORD in raw:
        active = True

        cleaned = raw.replace(WAKE_WORD, "").strip(",. ")

        if not cleaned:
            return "Yes?"

        return _process(cleaned)

    # -------------------------
    # ACTIVE MODE
    # -------------------------
    if active:
        response = _process(raw)

        # CRITICAL FIX:
        # auto-exit on goodbye
        if "going idle" in response.lower():
            active = False

        return response

    # -------------------------
    # PASSIVE MODE
    # -------------------------
    if any(x in raw for x in ["time", "date", "joke", "weather"]):
        return _process(raw)

    return ""

def reset():
    """
    CI / test isolation hook
    Resets conversational state
    """
    global active
    active = False