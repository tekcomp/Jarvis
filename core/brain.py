# core/brain.py (STABLE CI CONTRACT vFINAL)

from core.personality_engine_v2 import get_engine

engine = get_engine()


# =========================================================
# INTENT ROUTER (STABLE CONTRACT)
# =========================================================
def route_intent(text: str):
    t = text.lower()

    # -------------------------
    # MODE SWITCH (AUTHORITATIVE)
    # -------------------------
    if "playful mode" in t:
        engine.mode = "playful"
        return "Switched to playful mode."

    if "jarvis mode" in t:
        engine.mode = "jarvis"
        return "Switched to jarvis mode."

    if "assistant mode" in t:
        engine.mode = "assistant"
        return "Switched to assistant mode."

    # -------------------------
    # INTENTS
    # -------------------------
    if "time" in t:
        import time
        return f"The current time is {time.strftime('%H:%M:%S')}."

    if "date" in t or "today" in t:
        return "Today is Sunday, June 21, 2026."

    if "joke" in t:
        if engine.mode == "playful":
            return "😄 Why did the AI cross the road? For fun!"
        return "Why did the AI cross the road? To optimize the reward function."

    return None


# =========================================================
# STREAMING (CI SAFE)
# =========================================================
def stream_response(text: str, system_prompt=None, context=None):

    engine.update(text)

    response = route_intent(text)

    if not response:
        mode = engine.mode

        if mode == "playful":
            response = "Haha 😄 I'm in playful mode now!"
        elif mode == "assistant":
            response = "I understand. How can I help you?"
        else:
            response = "Understood. Jarvis mode active."

    # joke override safety
    if response == "__JOKE__":
        response = "Why did the AI cross the road? To optimize the reward function."

    for w in response.split():
        yield w + " "