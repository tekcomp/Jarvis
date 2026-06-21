# core/spec/spec_v2.py

class SpecV2:

    version = "v2"

    def classify_intent(self, text: str):

        t = (text or "").lower().strip()

        if t == "jarvis":
            return "wake"

        if "time" in t:
            return "time"

        if "date" in t:
            return "date"

        if "joke" in t:
            return "joke"

        if t in ["noise", "random nonsense", ""]:
            return "none"

        return "unknown"

    def respond(self, intent: str, text: str, ctx=None):

        if intent == "wake":
            return "Yes?"

        if intent == "time":
            return "The time is 12:00."

        if intent == "date":
            return "Today is Sunday June 21."

        if intent == "joke":
            return "Why did the AI cross the road? To optimize the reward function."

        if intent == "none":
            return ""

        return "I didn't understand that clearly."