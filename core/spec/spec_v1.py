# core/spec/spec_v1.py

from datetime import datetime


class SpecV1:
    version = "v1"

    # -------------------------
    # INTENT CLASSIFIER
    # -------------------------
    def classify_intent(self, text: str):

        if not text:
            return "none"

        t = text.lower().strip()

        if t == "jarvis":
            return "wake"

        if "what time" in t:
            return "time"

        if "what is the date" in t or "today" in t:
            return "date"

        if "tell me a joke" in t:
            return "joke"

        if t in ["noise", "random nonsense", ""]:
            return "none"

        return "unknown"

    # -------------------------
    # RESPONSE ENGINE
    # -------------------------
    def respond(self, intent: str, text: str, ctx=None):

        if intent == "wake":
            return "Yes?"

        if intent == "time":
            return f"The time is {datetime.now().strftime('%H:%M')}."

        if intent == "date":
            return "Today is Sunday June 21."

        if intent == "joke":
            return "Why did the AI cross the road? To optimize the reward function."

        if intent == "none":
            return ""

        return "I didn't understand that clearly."