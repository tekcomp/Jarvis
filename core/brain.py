# ==============================
# core/brain.py (PURE LOGIC LAYER v4)
# ==============================

import datetime

_state = {}


def reset():
    global _state
    _state = {}


def generate_response(text: str) -> str:

    t = text.lower().strip()

    if "time" in t:
        now = datetime.datetime.now().strftime("%H:%M:%S")
        return f"The time is {now}."

    if "date" in t or "today" in t:
        today = datetime.datetime.now().strftime("%A, %B %d, %Y")
        return f"Today is {today}."

    if "joke" in t:
        return "Why did the AI cross the road? To optimize the reward function."

    return f"You said: {text}"


def stream_response(text: str):

    response = generate_response(text)

    for token in response.split():
        yield token + " "