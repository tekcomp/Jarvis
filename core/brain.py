from datetime import datetime
from collections import deque
from core.memory import add

# =========================================================
# CONFIG
# =========================================================
WAKE_WORD = "jarvis"

active = False

# lightweight context window (last N turns)
context_window = deque(maxlen=6)


# =========================================================
# MEMORY HELPERS
# =========================================================
def _remember(role: str, text: str):
    """
    Stores structured conversation context
    """
    entry = f"{role}: {text}"
    context_window.append(entry)
    add(role, text)


def _get_context() -> str:
    """
    Returns short rolling context (future LLM-ready)
    """
    return "\n".join(context_window)


# =========================================================
# INTENT ENGINE
# =========================================================
def _process(text: str) -> str:

    text = text.strip().lower()

    _remember("user", text)

    response = None

    # -------------------------
    # TIME
    # -------------------------
    if "time" in text:
        response = f"The time is {datetime.now().strftime('%H:%M')}."

    # -------------------------
    # DATE
    # -------------------------
    elif "date" in text:
        response = f"Today is {datetime.now().strftime('%A %B %d')}."

    # -------------------------
    # JOKE
    # -------------------------
    elif "joke" in text:
        response = "Why did the AI cross the road? To optimize the reward function."

    # -------------------------
    # WEATHER (stub)
    # -------------------------
    elif "weather" in text:
        response = "Weather module not connected yet."

    # -------------------------
    # EXIT
    # -------------------------
    elif any(x in text for x in ["bye", "goodbye", "stop listening"]):
        response = "Going idle."

        global active
        active = False

    # -------------------------
    # UNKNOWN
    # -------------------------
    else:
        response = "I didn't understand that clearly."

    _remember("assistant", response)

    return response


# =========================================================
# ENTRY POINT (Cognitive Router)
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

        if not cleaned:
            response = "Yes?"
            _remember("assistant", response)
            return response

        return _process(cleaned)

    # =====================================================
    # ACTIVE MODE (FULL CONVERSATION)
    # =====================================================
    if active:
        return _process(raw)

    # =====================================================
    # PASSIVE MODE (LIGHT ROUTING ONLY)
    # =====================================================
    if any(x in raw for x in ["time", "date", "joke", "weather"]):
        return _process(raw)

    return ""