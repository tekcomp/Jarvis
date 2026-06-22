from core.personality_engine_v2 import get_engine
from core.brain import route_intent

engine = get_engine()


# =========================================================
# CI ENTRYPOINT
# =========================================================
def handle(text: str):

    engine.update(text)

    response = route_intent(text)

    if response:
        return response

    # ONLY SAFE FALLBACK
    if engine.mode == "playful":
        return "Haha 😄 I'm having fun!"

    if engine.mode == "assistant":
        return "I understand. How can I help you?"

    return "Understood."


# =========================================================
# RESET
# =========================================================
def reset():
    try:
        engine.reset()
    except Exception:
        pass


# =========================================================
# STREAM WRAPPER
# =========================================================
def stream(text: str):
    return stream_response(text)