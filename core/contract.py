from core.brain_v3 import classify_intent, update_state, generate_response
from core.personality_engine_v2 import get_engine

engine = get_engine()


def handle(text: str):

    intent = classify_intent(text)

    # update state first
    mode_change = update_state(intent, text)

    if mode_change:
        return mode_change

    # generate response
    return generate_response(intent, text)


def reset():
    engine.reset()