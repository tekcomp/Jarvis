from core.intent import score_intent
from datetime import datetime


def fallback_response(text: str) -> str:
    """
    Tier 3: conversational fallback (NOT command execution)
    """

    text = text.lower()

    if any(x in text for x in ["i love you", "love you"]):
        return "I appreciate that."

    if "hello" in text:
        return "Hello, I am online."

    if "how are you" in text:
        return "I am operating normally."

    if "what can you do" in text:
        return "I can tell time, date, jokes, and basic commands."

    return "I didn't understand that clearly."


def handle(text: str) -> str:

    result = score_intent(text)

    # -------------------------
    # TIER 1: STRONG INTENT
    # -------------------------
    if result.confidence >= 0.75:

        intent = result.intent

        if intent == "time":
            return f"The time is {datetime.now().strftime('%H:%M')}."

        if intent == "date":
            return f"Today is {datetime.now().strftime('%A %B %d')}."

        if intent == "joke":
            return "Why did the AI cross the road? To optimize the reward function."

        if intent == "weather":
            return "Weather module not connected yet."

    # -------------------------
    # TIER 2: WEAK INTENT (RECOVERY)
    # -------------------------
    if 0.45 <= result.confidence < 0.75:

        if result.intent == "time":
            return f"The time is {datetime.now().strftime('%H:%M')}."

        if result.intent == "date":
            return f"Today is {datetime.now().strftime('%A %B %d')}."

        if result.intent == "joke":
            return "Why did the AI cross the road? To optimize the reward function."

    # -------------------------
    # TIER 3: FALLBACK CHAT
    # -------------------------
    return fallback_response(result.cleaned)