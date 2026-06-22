import re
from core.personality_engine_v2 import get_engine


engine = get_engine()


# =========================================================
# 1. INTENT CLASSIFIER (RULE-BASED v1 → upgradeable later)
# =========================================================
def classify_intent(text: str):

    t = text.lower()

    # ---- MODE SWITCHING (HIGH PRIORITY) ----
    if re.search(r"\b(playful|fun|joke mode)\b", t):
        return {"type": "mode", "value": "playful"}

    if re.search(r"\b(jarvis|serious|formal)\b", t):
        return {"type": "mode", "value": "jarvis"}

    if re.search(r"\b(assistant|help mode)\b", t):
        return {"type": "mode", "value": "assistant"}

    # ---- TASK INTENTS ----
    if "time" in t:
        return {"type": "info", "value": "time"}

    if "date" in t or "today" in t:
        return {"type": "info", "value": "date"}

    if "joke" in t:
        return {"type": "fun", "value": "joke"}

    return {"type": "unknown", "value": None}


# =========================================================
# 2. STATE UPDATE LAYER
# =========================================================
def update_state(intent, text):

    if intent["type"] == "mode":
        engine.mode = intent["value"]
        return f"Switched to {engine.mode} mode."

    engine.update(text)
    return None


# =========================================================
# 3. RESPONSE POLICY ENGINE
# =========================================================
def generate_response(intent, text):

    mode = engine.mode

    # ---- MODE BEHAVIOR ----
    if intent["type"] == "info" and intent["value"] == "time":
        import time
        return f"The current time is {time.strftime('%H:%M:%S')}."

    if intent["type"] == "info" and intent["value"] == "date":
        import datetime
        now = datetime.datetime.now()
        return now.strftime("%A, %B %d, %Y")

    if intent["type"] == "fun" and intent["value"] == "joke":
        if mode == "playful":
            return "😄 Why did the AI cross the road? For fun!"
        return "Why did the AI cross the road? To optimize the reward function."

    # ---- MODE DEFAULT BEHAVIOR ----
    if mode == "playful":
        return "Haha 😄 I'm in playful mode!"

    if mode == "assistant":
        return "How can I help you?"

    if mode == "jarvis":
        return "I require more information, sir."

    return "I am ready."