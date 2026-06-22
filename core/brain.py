from core.personality_engine_v2 import get_engine
from core.mode_parser import detect_mode
import datetime

# =========================================================
# SINGLE SOURCE OF TRUTH
# =========================================================
engine = get_engine()


# =========================================================
# INTENT ROUTER
# =========================================================
def route_intent(text: str):

    t = text.lower()

    # --------------------------
    # MODE SWITCH
    # --------------------------
    mode = detect_mode(text)

    if mode:
        engine.mode = mode
        return None

    # --------------------------
    # INTENTS
    # --------------------------
    if "time" in t:
        now = datetime.datetime.now()
        return f"The current time is {now.strftime('%H:%M:%S')}."

    if "date" in t or "today" in t:
        return datetime.datetime.now().strftime("%A, %B %d, %Y")

    if "joke" in t:
        return "__JOKE__"

    return None


# =========================================================
# STREAM RESPONSE
# =========================================================
def stream_response(text: str, system_prompt=None, context=None):

    engine.update(text)

    response = route_intent(text)

    # --------------------------
    # MODE-AWARE FALLBACK
    # --------------------------
    if not response:

        mode = engine.mode

        if mode == "playful":
            response = "Haha 😄 I'm in playful mode now!"
        elif mode == "assistant":
            response = "I understand. How can I help you?"
        elif mode == "jarvis":
            response = "Understood. Jarvis mode active."
        else:
            response = "I am online."

    # --------------------------
    # JOKE OVERRIDE
    # --------------------------
    if response == "__JOKE__":

        if engine.mode == "playful":
            response = "😄 Why did the AI cross the road? For fun!"
        else:
            response = "Why did the AI cross the road? To optimize the reward function."

    for w in response.split():
        yield w + " "