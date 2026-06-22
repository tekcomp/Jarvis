class ModeStateMachine:

    def __init__(self):
        self.mode = "jarvis"

    def detect(self, text: str):

        t = text.lower()

        if "playful" in t or "fun" in t:
            return "playful"

        if "assistant" in t:
            return "assistant"

        if "jarvis" in t:
            return "jarvis"

        return None

    def apply(self, mode: str):
        self.mode = mode