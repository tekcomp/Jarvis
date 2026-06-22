from dataclasses import dataclass
import time

# =========================================================
# STATE
# =========================================================
@dataclass
class PersonalityState:
    mode: str = "jarvis"
    mood: str = "neutral"
    emotion: str = "neutral"
    emotion_strength: float = 0.0
    last_update: float = 0.0


# =========================================================
# ENGINE SINGLETON
# =========================================================
_ENGINE = None


def get_engine():
    global _ENGINE
    if _ENGINE is None:
        _ENGINE = PersonalityEngineV2()
    return _ENGINE


# =========================================================
# ENGINE
# =========================================================
class PersonalityEngineV2:

    def __init__(self):
        self.state = PersonalityState()
        self.history = []

    # -------------------------
    # SAFE ACCESSORS
    # -------------------------
    @property
    def mode(self):
        return self.state.mode

    @mode.setter
    def mode(self, value):
        self.state.mode = value

    @property
    def mood(self):
        return self.state.mood

    @mood.setter
    def mood(self, value):
        self.state.mood = value

    # -------------------------
    # UPDATE
    # -------------------------
    def update(self, text: str):
        if not text:
            return

        text = text.lower().strip()

        self.history.append(text)
        if len(self.history) > 12:
            self.history.pop(0)

        self.state.last_update = time.time()

    # -------------------------
    # SNAPSHOT
    # -------------------------
    def snapshot(self):
        return {
            "mode": self.state.mode,
            "mood": self.state.mood,
            "emotion": self.state.emotion,
        }

    # -------------------------
    # RESET
    # -------------------------
    def reset(self):
        self.state = PersonalityState()
        self.history.clear()
    
    # REQUIRED FOR CI COMPATIBILITY
    def get_engine():
        global _ENGINE_SINGLETON
        if _ENGINE_SINGLETON is None:
            _ENGINE_SINGLETON = PersonalityEngineV2()
        return _ENGINE_SINGLETON
    
    def system_prompt(self):
        base = "You are Jarvis."

        if self.state.mode == "assistant":
            base = "You are a professional AI assistant."
        elif self.state.mode == "playful":
            base = "You are a friendly playful AI."

        emotion = self.state.emotion

        if emotion == "frustrated":
            tone = "User is frustrated. Respond calmly and clearly."
        elif emotion == "excited":
            tone = "User is excited. Match energy slightly."
        else:
            tone = "Maintain neutral tone."

        return f"""



{base}

{tone}

Mode: {self.state.mode}
Emotion: {self.state.emotion}
Emotion Strength: {self.state.emotion_strength:.2f}

Keep responses voice-friendly and concise.
"""