# core/personality_engine_v2.py


# ==========================================
# core/personality_engine_v2.py
# Personality Engine v2
# Production Ready
# ==========================================

from dataclasses import dataclass
import time


@dataclass
class PersonalityState:
    mode: str = "jarvis"
    mood: str = "neutral"
    last_update: float = 0.0


class PersonalityEngineV2:

    def __init__(self):

        self.state = PersonalityState()

        self.history = []

        self.max_history = 10

    # ==========================================
    # UPDATE
    # ==========================================
    def update(self, text: str):
        
        text = text.replace(".", "").replace(",", "").strip()

        if not text:
            return

        text = text.lower().strip()

        self._track_history(text)

        self._check_mode_switch(text)

        self._detect_mood(text)

        self.state.last_update = time.time()

    # ==========================================
    # HISTORY
    # ==========================================
    def _track_history(self, text):

        self.history.append(text)

        if len(self.history) > self.max_history:
            self.history.pop(0)

    # ==========================================
    # MODE SWITCHING
    # ==========================================
    def _check_mode_switch(self, text):

        if "assistant mode" in text:
            self.state.mode = "assistant"

        elif "playful mode" in text:
            self.state.mode = "playful"

        elif "jarvis mode" in text:
            self.state.mode = "jarvis"

    # ==========================================
    # MOOD DETECTION
    # ==========================================
    def _detect_mood(self, text):

        if any(word in text for word in [
            "sad",
            "upset",
            "depressed",
            "frustrated",
            "angry"
        ]):
            self.state.mood = "supportive"

        elif any(word in text for word in [
            "excited",
            "awesome",
            "great",
            "happy"
        ]):
            self.state.mood = "positive"

        else:
            self.state.mood = "neutral"

    # ==========================================
    # MODE PROMPTS
    # ==========================================
    def _assistant_prompt(self):

        return """
You are a professional AI assistant.

Rules:
- Be concise.
- Be accurate.
- Be direct.
- Prefer short answers.
- Avoid unnecessary humor.
"""

    def _playful_prompt(self):

        return """
You are a friendly and playful AI assistant.

Rules:
- Be warm.
- Add light humor when appropriate.
- Sound conversational.
- Keep responses voice-friendly.
- Never be annoying.
"""

    def _jarvis_prompt(self):

        return """
You are Jarvis.

Rules:
- Speak elegantly.
- Be intelligent.
- Be confident.
- Sound calm and capable.
- Use short sophisticated responses.
- Avoid lengthy explanations unless requested.
"""

    # ==========================================
    # MOOD OVERLAY
    # ==========================================
    def _mood_overlay(self):

        if self.state.mood == "supportive":

            return """
User may be frustrated.
Respond with empathy and patience.
"""

        if self.state.mood == "positive":

            return """
User appears enthusiastic.
Match positive energy.
"""

        return ""

    # ==========================================
    # SYSTEM PROMPT
    # ==========================================
    def system_prompt(self):

        if self.state.mode == "assistant":
            base = self._assistant_prompt()

        elif self.state.mode == "playful":
            base = self._playful_prompt()

        else:
            base = self._jarvis_prompt()

        mood = self._mood_overlay()

        return f"""
{base}

{mood}

Current Mode:
{self.state.mode}

Current Mood:
{self.state.mood}

Keep answers optimized for voice conversations.
"""

    # ==========================================
    # PUBLIC HELPERS
    # ==========================================
    def mode(self):
        return self.state.mode

    def mood(self):
        return self.state.mood

    def snapshot(self):

        return {
            "mode": self.state.mode,
            "mood": self.state.mood,
            "history_size": len(self.history)
        }

    def reset(self):

        self.state = PersonalityState()
        self.history.clear()

