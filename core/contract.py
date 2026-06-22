from core.personality_engine_v2 import get_engine
from core.brain import route_intent

engine = get_engine()


def handle(text: str):

    engine.update(text)

    response = route_intent(text)

    if response:
        return response

    mode = engine.mode

    if mode == "playful":
        return "Haha 😄 I'm having fun!"
    elif mode == "assistant":
        return "How can I help you?"
    else:
        return "Understood. Jarvis mode active."


def reset():
    engine.reset()