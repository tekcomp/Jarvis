# ==============================
# core/brain.py (CIRCULAR IMPORT FIXED)
# ==============================

import time


def stream_response(text: str):
    """
    SIMPLE STREAM ENGINE (NO SELF IMPORTS)
    """

    text = (text or "").lower()

    # simulate streaming tokens
    response = route_response(text)

    for word in response.split():
        yield word + " "
        time.sleep(0.01)


def route_response(text: str) -> str:
    """
    DETERMINE RESPONSE WITHOUT IMPORTING ANYTHING FROM brain.py
    (THIS FIXES CIRCULAR IMPORT)
    """

    # TIME
    if "time" in text:
        return f"The time is {time.strftime('%H:%M:%S')}."

    # DATE
    if "date" in text or "today" in text:
        return time.strftime("Today is %A, %B %d, %Y.")

    # JOKE
    if "joke" in text:
        return "Why did the AI cross the road? To optimize the reward function."

    # DEFAULT
    return f"You said: {text}"