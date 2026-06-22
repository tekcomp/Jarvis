from core.personality_engine_v2 import get_engine
from core.mode_parser import detect_mode
import datetime

# =========================================================
# SINGLE ENGINE
# =========================================================
engine = get_engine()


# =========================================================
# INTENT ROUTER
# =========================================================
def route_intent(text: str):

    t = text.lower()

    # --------------------------
    # MODE SWITCH (HIGHEST PRIORITY)
    # --------------------------
    mode = detect_mode(text)

    if mode:

        engine.mode = mode

        # 🔥 IMPORTANT: return IMMEDIATELY so fallback cannot override
        return f"Switched to {mode} mode."

    # --------------------------
    # INTENTS
    # --------------------------
    if "time" in t:
        now = datetime.datetime.now()
        return f"The current time is {now.strftime('%H:%M:%S')}."

    if "date" in t or "today" in t:
        return datetime.datetime.now().strftime("%A, %B %d, %Y")

    if "joke" in t:
        if engine.mode == "playful":
            return "Haha 😄 Why did the AI cross the road? For fun!"
        return "Why did the AI cross the road? To optimize the reward function."

    return None


# =========================================================
# STREAM RESPONSE (SINGLE TRUTH PATH)
# =========================================================
def stream_response(text: str, system_prompt=None, context=None):

    engine.update(text)

    response = route_intent(text)

    # --------------------------
    # CLEAN MODE FALLBACK (ONLY HERE)
    # --------------------------
    if response is None:

        mode = engine.mode

        if mode == "playful":
            response = "Haha 😄 I'm in playful mode!"
        elif mode == "assistant":
            response = "I understand. How can I help you?"
        elif mode == "jarvis":
            response = "Understood. Jarvis mode active."
        else:
            response = "I am online."

    # --------------------------
    # STREAM
    # --------------------------
    for word in response.split():
        yield word + " "