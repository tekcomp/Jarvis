import time
from dataclasses import dataclass, field


# =========================================================
# STATE MODEL
# =========================================================
@dataclass
class PersonalityState:

    mood: str = "neutral"          # neutral | focused | playful
    verbosity: float = 0.5         # 0.0 short → 1.0 verbose

    last_intent: str = ""
    last_user_text: str = ""

    last_interaction_ts: float = field(default_factory=time.time)

    interrupted: bool = False

    def age(self):
        return time.time() - self.last_interaction_ts


# =========================================================
# INTENT CLASSIFIER (LIGHTWEIGHT, NO ML DEPENDENCY)
# =========================================================
def classify(text: str) -> dict:

    t = text.lower()

    intent = "unknown"
    mood = "neutral"

    # INTENTS
    if "time" in t:
        intent = "query_time"
    elif "date" in t:
        intent = "query_date"
    elif "joke" in t:
        intent = "joke"
    elif "stop" in t:
        intent = "interrupt"

    # MOOD SIGNALS
    if "?" in t:
        mood = "curious"
    if "joke" in t:
        mood = "playful"
    if "now" in t:
        mood = "focused"

    return {
        "intent": intent,
        "mood": mood
    }


# =========================================================
# PERSONALITY ENGINE v2 (CORE)
# =========================================================
class PersonalityEngineV2:

    def __init__(self):
        self.state = PersonalityState()

    # -----------------------------------------------------
    # UPDATE FROM USER INPUT
    # -----------------------------------------------------
    def update(self, text: str):

        result = classify(text)

        self.state.last_user_text = text
        self.state.last_intent = result["intent"]
        self.state.last_interaction_ts = time.time()

        # mood shaping
        if result["mood"] == "playful":
            self.state.mood = "playful"
            self.state.verbosity = 0.6

        elif result["mood"] == "focused":
            self.state.mood = "focused"
            self.state.verbosity = 0.3

        else:
            self.state.mood = "neutral"
            self.state.verbosity = 0.5

        return self.state

    # -----------------------------------------------------
    # INTERRUPT HANDLING
    # -----------------------------------------------------
    def on_interrupt(self):
        self.state.interrupted = True
        self.state.mood = "focused"
        self.state.verbosity = 0.2

    def clear_interrupt(self):
        self.state.interrupted = False

    # -----------------------------------------------------
    # RESPONSE STYLE ENGINE
    # -----------------------------------------------------
    def style_instruction(self) -> str:

        if self.state.mood == "focused":
            return "Be extremely concise. One sentence max."

        if self.state.mood == "playful":
            return "Be witty but brief. Light humor allowed."

        return "Be natural, helpful, conversational."

    # -----------------------------------------------------
    # SYSTEM PROMPT BUILDER (IMPORTANT)
    # -----------------------------------------------------
    def system_prompt(self) -> str:

        return f"""
You are Jarvis, a real-time voice AI assistant.

Personality State:
- Mood: {self.state.mood}
- Verbosity: {self.state.verbosity}
- Last Intent: {self.state.last_intent}

Rules:
- {self.style_instruction()}
- Never be overly verbose unless asked
- Respond in spoken conversational format
- Stay context-aware across turns
"""