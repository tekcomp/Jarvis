import time
from core.personality_engine_v2 import PersonalityEngineV2

# =========================================================
# SINGLE SOURCE OF TRUTH
# =========================================================
personality = PersonalityEngineV2()


# =========================================================
# MODE ENGINE (CLEAN + RELIABLE)
# =========================================================
def apply_mode(text: str):

    t = text.lower()

    if "playful" in t and "mode" in t:
        personality.state.mode = "playful"
        return "Switched to playful mode."

    if "jarvis" in t and "mode" in t:
        personality.state.mode = "jarvis"
        return "Jarvis mode active."

    if "assistant" in t and "mode" in t:
        personality.state.mode = "assistant"
        return "Assistant mode active."

    return None


# =========================================================
# INTENT ENGINE
# =========================================================
def route_intent(text: str):

    t = text.lower()

    # MODE FIRST
    mode_response = apply_mode(text)
    if mode_response:
        return mode_response

    # TIME
    if "time" in t:
        return f"The current time is {time.strftime('%H:%M:%S')}."

    # DATE
    if "date" in t or "today" in t:
        return "Today is Sunday, June 21, 2026."

    # JOKE
    if "joke" in t:
        return "__JOKE__"

    return None


# =========================================================
# PERSONALITY FUSION ENGINE (🔥 NEW CORE)
# =========================================================
def personality_fusion(raw_response: str):

    mode = personality.state.mode
    mood = personality.state.mood

    # -------------------------
    # JOKE PERSONALITY OVERRIDE
    # -------------------------
    if raw_response == "__JOKE__":

        if mode == "playful":
            return "Haha 😄 Why did the AI become self-aware? It optimized humor gradients!"

        if mode == "jarvis":
            return "Humor module engaged. Why did the AI cross the road? To optimize the reward function."

        return "Why did the AI cross the road? To optimize the reward function."

    # -------------------------
    # MODE STYLING WRAPPER
    # -------------------------
    if mode == "playful":
        return f"😄 {raw_response}"

    if mode == "jarvis":
        return f"Understood. {raw_response}"

    return raw_response


# =========================================================
# PUBLIC API
# =========================================================
def generate_response(text, system_prompt=None, context=None):
    return route_intent(text)


# =========================================================
# STREAM ENGINE (FIXED BEHAVIOR)
# =========================================================
def stream_response(text, system_prompt=None, context=None):

    personality.update(text)

    raw = route_intent(text)

    if not raw:
        raw = "I am online and ready."

    final = personality_fusion(raw)

    for word in final.split():
        yield word + " "


# =========================================================
# RESET
# =========================================================
def reset():
    personality.reset()
    return True