from core.personality_engine_v2 import get_engine
from core.holiday_engine import get_holidays

engine = get_engine()


def route_intent(text: str):

    t = text.lower()

    # -------------------------
    # MODE SWITCH
    # -------------------------
    if "playful mode" in t:
        engine.mode = "playful"
        return "Switched to playful mode."

    if "jarvis" in t:
        engine.mode = "jarvis"
        return "Jarvis mode activated."

    if "jarvis mode" in t:
        engine.mode = "jarvis"
        return "Switched to jarvis mode."

    if "assistant" in t:
        engine.mode = "assistant"
        return "Assistant mode activated."

    if "assistant mode" in t:
        engine.mode = "assistant"
        return "Switched to assistant mode."

    # -------------------------
    # HOLIDAYS
    # -------------------------

    if "january" in t:
        return get_holidays("january")

    if "february" in t:
        return get_holidays("february")

    if "march" in t:
        return get_holidays("march")

    if "april" in t:
        return get_holidays("april")

    if "may" in t:
        return get_holidays("may")

    if "june" in t:
        return get_holidays("june")

    if "july" in t:
        return get_holidays("july")

    if "august" in t:
        return get_holidays("august")

    if "september" in t:
        return get_holidays("september")

    if "october" in t:
        return get_holidays("october")

    if "november" in t:
        return get_holidays("november")

    if "december" in t:
        return get_holidays("december")

    if "bye" in t:
        if engine.mode == "playful":
            return "Haha 😄 See you next time!"
        elif engine.mode == "assistant":
            return "Goodbye! Let me know if you need anything else."
        else:
            return "Goodbye!"

    if "time" in t:
        import time
        return f"The current time is {time.strftime('%H:%M:%S')}."

    if "date" in t or "today" in t:
        return "Today is Sunday, June 21, 2026."

    if "joke" in t:
        if engine.mode == "playful":
            return "😄 Why did the AI cross the road? For fun!"
        return "Why did the AI cross the road? To optimize the reward function."


def stream_response(text: str, system_prompt=None, context=None):

    engine.update(text)

    # ❗ IMPORTANT: ONLY CALL route_intent ONCE
    response = route_intent(text)

    if not response:

        mode = engine.mode

        if mode == "playful":
            response = "Haha 😄 I'm in playful mode!"
        elif mode == "assistant":
            response = "How can I help you?"
        else:
            response = "Understood. Jarvis mode active."

    for w in response.split():
        yield w + " "