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
# SINGLETON HOLDER
# =========================================================
_ENGINE_SINGLETON = None


# =========================================================
# ENGINE
# =========================================================
class PersonalityEngineV2:

    def __init__(self):
        self.state = PersonalityState()
        self.history = []
        self.max_history = 12

    # =====================================================
    # COMPAT: MODE ACCESS
    # =====================================================
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

    # =====================================================
    # UPDATE
    # =====================================================
    def update(self, text: str):

        if not text:
            return

        text = text.lower().strip()

        self.history.append(text)

        if len(self.history) > self.max_history:
            self.history.pop(0)

        self.state.last_update = time.time()

        self._detect_mood(text)
        self._detect_emotion(text)

    # =====================================================
    # MODE-AWARE PROMPT (🔥 THIS WAS MISSING)
    # =====================================================
    def system_prompt(self):

        if self.state.mode == "playful":
            base = "You are a friendly playful AI."
        elif self.state.mode == "assistant":
            base = "You are a helpful AI assistant."
        else:
            base = "You are Jarvis, a precise assistant."

        emotion = self._emotion_bias()

        if emotion == "calm":
            emo_text = "User may be frustrated. Be calm and supportive."
        elif emotion == "energy":
            emo_text = "User is excited. Match energy slightly."
        else:
            emo_text = "Maintain neutral tone."

        return f"""
{base}

{emo_text}

Mode: {self.state.mode}
Emotion: {self.state.emotion}
Strength: {self.state.emotion_strength:.2f}
""".strip()

    # =====================================================
    # EMOTION
    # =====================================================
    def _detect_mood(self, text):

        if any(w in text for w in ["sad", "angry", "frustrated"]):
            self.state.mood = "supportive"
        elif any(w in text for w in ["happy", "great", "awesome"]):
            self.state.mood = "positive"
        else:
            self.state.mood = "neutral"

    def _detect_emotion(self, text):

        if any(w in text for w in ["error", "broken", "fix", "stuck"]):
            self.state.emotion = "frustrated"
            self.state.emotion_strength = min(1.0, self.state.emotion_strength + 0.3)

        elif any(w in text for w in ["wow", "cool", "love", "awesome"]):
            self.state.emotion = "excited"
            self.state.emotion_strength = min(1.0, self.state.emotion_strength + 0.2)

        else:
            self.state.emotion_strength *= 0.85

            if self.state.emotion_strength < 0.2:
                self.state.emotion = "neutral"

    def _emotion_bias(self):

        if self.state.emotion == "frustrated":
            return "calm"
        if self.state.emotion == "excited":
            return "energy"
        return "neutral"

    # =====================================================
    # RESET
    # =====================================================
    def reset(self):
        self.state = PersonalityState()
        self.history.clear()


# =========================================================
# SINGLETON
# =========================================================
def get_engine():
    global _ENGINE_SINGLETON
    if _ENGINE_SINGLETON is None:
        _ENGINE_SINGLETON = PersonalityEngineV2()
    return _ENGINE_SINGLETON