from enum import Enum

class Intent(str, Enum):
    TIME = "time"
    DATE = "date"
    JOKE = "joke"
    CHAT = "chat"
    UNKNOWN = "unknown"


def classify(text: str) -> Intent:
    t = text.lower()

    if "time" in t:
        return Intent.TIME

    if "date" in t or "day" in t:
        return Intent.DATE

    if "joke" in t:
        return Intent.JOKE

    return Intent.CHAT