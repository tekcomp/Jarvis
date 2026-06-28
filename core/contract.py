from core.personality_engine_v2 import get_engine
from core.brain import route_intent

engine = get_engine()


def handle(text: str):
    engine.update(text)
    response = route_intent(text)

    if response is not None:
        return response

    # Return empty string for unrecognized intents (noise, invalid input)
    return ""


def reset():
    engine.reset()