from datetime import datetime
import re


def clean(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^\w\s]", "", text)
    return text.strip()


def handle(text: str) -> str:

    text = clean(text)

    # -----------------------
    # WAKE WORD
    # -----------------------
    if "jarvis" in text:
        return "Yes sir."

    # -----------------------
    # TIME
    # -----------------------
    if "time" in text:
        return f"The time is {datetime.now().strftime('%H:%M')}."

    # -----------------------
    # DATE
    # -----------------------
    if "date" in text or "today" in text:
        return f"Today is {datetime.now().strftime('%A %B %d')}."

    # -----------------------
    # CAPITAL OF FLORIDA
    # -----------------------
    if "capital" in text and "florida" in text:
        return "The capital of Florida is Tallahassee."

    # -----------------------
    # JOKE
    # -----------------------
    if "joke" in text:
        return "Why did the AI cross the road? To optimize the reward function."

    # -----------------------
    # FALLBACK
    # -----------------------
    return "I didn't understand that."