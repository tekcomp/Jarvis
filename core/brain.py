from core.personality_engine_v2 import get_engine
from core.mode_parser import detect_mode

personality = get_engine()


def route_intent(text: str):

    t = text.lower()

    # --------------------------
    # MODE SWITCH (FIXED)
    # --------------------------
    mode = detect_mode(text)

    if mode:
        personality.mode = mode
        return f"Switched to {mode} mode."

    # --------------------------
    # INTENTS
    # --------------------------
    if "time" in t:
        import time
        return f"The current time is {time.strftime('%H:%M:%S')}."

    if "date" in t or "today" in t:
        return "Today is Sunday, June 21, 2026."

    if "joke" in t:
        if personality.mode == "playful":
            return "Haha 😄 Why did the AI cross the road? For fun!"
        return "Why did the AI cross the road? To optimize the reward function."

    return None


def stream_response(text: str, system_prompt=None, context=None):

    personality.update(text)

    response = route_intent(text)

    if not response:
        mode = personality.mode

        if mode == "playful":
            response = "Haha 😄 I'm in playful mode!"
        elif mode == "assistant":
            response = "How can I help you?"
        else:
            response = "I am online."

    for w in response.split():
        yield w + " "