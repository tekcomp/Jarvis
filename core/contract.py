from core.personality_engine_v2 import get_engine
from core.brain import route_intent

# SINGLE SOURCE OF TRUTH
personality = get_engine()


# =========================================================
# MAIN ENTRYPOINT (CI USES THIS)
# =========================================================
def handle(text: str):

    personality.update(text)

    response = route_intent(text)

    if response and response.strip():
        return response

    # fallback MUST be mode-aware
    mode = personality.mode

    if mode == "playful":
        return "Haha 😄 I'm in playful mode!"

    if mode == "jarvis":
        return "I require more information, sir."

    if mode == "assistant":
        return "I understand. How can I help you?"

    return "I am ready."


# =========================================================
# RESET (FIX FOR TESTS)
# =========================================================
def reset():
    """
    CI EXPECTS THIS FUNCTION.
    MUST EXIST AT MODULE LEVEL.
    """
    try:
        personality.reset()
    except Exception:
        pass

    return True


# =========================================================
# STREAM WRAPPER (OPTIONAL)
# =========================================================
def stream(text: str):
    from core.brain import stream_response
    return stream_response(text)