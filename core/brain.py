import time
from core.personality_engine_v2 import PersonalityEngineV2

# =========================================================
# SINGLE SOURCE OF TRUTH
# =========================================================
personality = PersonalityEngineV2()


# =========================================================
# MODE SWITCHING (REAL EXECUTION)
# =========================================================
def apply_mode(text: str):

    t = text.lower()

    if "playful mode" in t:
        personality.state.mode = "playful"
        return "Switched to playful mode."

    if "jarvis mode" in t:
        personality.state.mode = "jarvis"
        return "Switched to jarvis mode."

    if "assistant mode" in t:
        personality.state.mode = "assistant"
        return "Switched to assistant mode."

    return None


# =========================================================
# INTENT ENGINE
# =========================================================
def route_intent(text: str):

    t = text.lower()

    # =========================
    # MODE SWITCHING (FIRST)
    # =========================
    mode_response = apply_mode(text)
    if mode_response:
        return mode_response

    # =========================
    # NORMAL INTENTS
    # =========================
    if "time" in t:
        return f"The current time is {time.strftime('%H:%M:%S')}."

    if "date" in t or "today" in t:
        return "Today is Sunday, June 21, 2026."

    if "joke" in t:
        if personality.state.mode == "playful":
            return "Haha 😄 Why did the AI become playful? It learned humor gradients!"
        return "Why did the AI cross the road? To optimize the reward function."

    return None


# =========================================================
# CI COMPATIBILITY
# =========================================================
def generate_response(text, system_prompt=None, context=None):
    return route_intent(text)


# =========================================================
# STREAM LAYER (FIXED BEHAVIOR)
# =========================================================
def stream_response(text, system_prompt=None, context=None):

    # UPDATE PERSONALITY FIRST (IMPORTANT)
    personality.update(text)

    response = route_intent(text)

    # MODE-AWARE FALLBACK (CRITICAL FIX)
    if not response:

        mode = personality.state.mode

        if mode == "playful":
            response = "Haha 😄 I'm in playful mode!"

        elif mode == "jarvis":
            response = "Understood. Jarvis mode active."

        else:
            response = "I am online and ready."

    for word in response.split():
        yield word + " "


# =========================================================
# RESET
# =========================================================
def reset():
    personality.reset()
    return True