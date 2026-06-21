from core.intent_router import classify, Intent
from core.policy import PolicyDecision
from core.memory import WorkingMemory
from core.brain import stream_response


class Agent:
    def __init__(self):
        self.memory = WorkingMemory()

    def step(self, text: str):
        intent = classify(text)

        self.memory.add(text)

        policy = self._decide(intent)

        if policy.should_use_tools:
            return self._tool_route(intent, text)

        return self._chat(text)

    def _decide(self, intent: Intent):
        if intent in (Intent.TIME, Intent.DATE):
            return PolicyDecision(True, False)

        return PolicyDecision(True, False)

    def _tool_route(self, intent, text):
        if intent == Intent.TIME:
            return "The time is now."

        if intent == Intent.DATE:
            return "Today is June 21, 2026."

        return ""

    def _chat(self, text):
        return "".join(stream_response(text))