from datetime import datetime
import re

WAKE_WORD = "jarvis"
active = False


# -------------------------
# CLEAN INPUT
# -------------------------
def _clean(text: str) -> str:
    """
    Removes wake word + noise + punctuation safely
    """
    text = text.lower().strip()

    # remove wake word
    text = text.replace(WAKE_WORD, "")

    # remove punctuation (more robust than before)
    text = re.sub(r"[^\w\s]", "", text)

    return text.strip()


# -------------------------
# SIMPLE CONFIDENCE SCORER
# -------------------------
def _confidence(text: str, keywords: list) -> float:
    """
    Lightweight scoring to prevent garbage triggers
    """
    score = 0.0

    for kw in keywords:
        if kw in text:
            score += 0.6

        # exact match bonus
        if text == kw:
            score += 0.3

        # word-level match bonus
        if kw in text.split():
            score += 0.1

    return min(score, 1.0)


# -------------------------
# MAIN ENTRY
# -------------------------
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

            # only wake word
            if cleaned == "":
                return "Yes?"

            return _process(cleaned)

        return ""  # ignore everything else

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
    # NOISE FILTER (IMPORTANT FIX)
    # -------------------------
    NOISE_BLOCK = ["darkness", "to this date", "the color is blue"]

    if any(x in cleaned for x in NOISE_BLOCK):
        return "I didn't understand that clearly."

    # -------------------------
    # NORMAL FLOW
    # -------------------------
    return _process(cleaned)


# -------------------------
# EXECUTION ENGINE
# -------------------------
def _process(text: str) -> str:

    text = text.strip()

    # TIME
    if _confidence(text, ["time", "clock", "what time"]) > 0.5:
        return f"The time is {datetime.now().strftime('%H:%M')}."

    # DATE
    if _confidence(text, ["date", "today", "what day"]) > 0.5:
        return f"Today is {datetime.now().strftime('%A %B %d')}."

    # JOKE
    if _confidence(text, ["joke", "funny", "laugh"]) > 0.5:
        return "Why did the AI cross the road? To optimize the reward function."

    # WEATHER
    if _confidence(text, ["weather", "temperature", "forecast"]) > 0.5:
        return "Weather module not connected yet."

    # GOODBYE
    if "goodbye" in text:
        return "Goodbye! Have a great day!"

    return "I didn't understand that clearly."