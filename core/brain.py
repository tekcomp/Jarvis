from datetime import datetime

WAKE_WORD = "jarvis"

_state = {
    "active": False
}


def reset():
    _state["active"] = False


# =========================================================
# CANONICAL NORMALIZER (ONLY SOURCE OF TRUTH)
# =========================================================
def _normalize(text: str) -> str:
    return (
        text.lower()
        .replace(WAKE_WORD, "")
        .replace("?", "")
        .replace(".", "")
        .replace("!", "")
        .strip()
    )


def _is_wake(text: str) -> bool:
    return WAKE_WORD in text.lower()


def _is_wake_only(text: str) -> bool:
    return _normalize(text) == ""


# =========================================================
# PROCESSOR
# =========================================================
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

    if any(x in text for x in ["bye", "goodbye", "stop"]):
        _state["active"] = False
        return "Going idle."

    return "I didn't understand that clearly."


# =========================================================
# ENTRY POINT
# =========================================================
def handle(text: str) -> str:

    if not text:
        return ""

    raw = text.lower().strip()

    wake_detected = _is_wake(raw)

    # =====================================================
    # IDLE MODE
    # =====================================================
    if not _state["active"]:

        if wake_detected:

            _state["active"] = True

            # STRICT CASE: wake-only
            if _is_wake_only(raw):
                return "Yes?"

            cleaned = _normalize(raw)
            return _process(cleaned)

        # passive mode
        if any(x in raw for x in ["time", "date", "joke", "weather"]):
            return _process(raw)

        return ""

    # =====================================================
    # ACTIVE MODE
    # =====================================================
    if _state["active"]:

        if wake_detected and _is_wake_only(raw):
            return "Yes?"

        if wake_detected:
            raw = _normalize(raw)

        return _process(raw)