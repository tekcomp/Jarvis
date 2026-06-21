from dataclasses import dataclass
from enum import Enum
from datetime import datetime
import random


# =========================
# INTENTS
# =========================
class Intent(str, Enum):
    TIME = "time"
    DATE = "date"
    JOKE = "joke"
    WAKE = "wake"
    SHUTDOWN = "shutdown"
    NOISE = "none"
    UNKNOWN = "unknown"


@dataclass
class ContractResult:
    intent: Intent
    normalized: str
    raw: str


# =========================
# CONTRACT CLASSIFIER (FIXED)
# =========================
class SpecContractV2:

    @staticmethod
    def classify(text: str) -> ContractResult:

        if not text or text.strip() == "":
            return ContractResult(Intent.NOISE, "", text)

        t = text.lower().strip()

        # WAKE WORD
        if "jarvis" == t:
            return ContractResult(Intent.WAKE, t, text)

        # TIME
        if "time" in t:
            return ContractResult(Intent.TIME, t, text)

        # DATE (IMPORTANT: separate from TIME)
        if "date" in t or "today's date" in t or "what day" in t:
            return ContractResult(Intent.DATE, t, text)

        # JOKE
        if "joke" in t:
            return ContractResult(Intent.JOKE, t, text)

        # SHUTDOWN
        if t in ["bye", "exit", "quit", "shutdown"]:
            return ContractResult(Intent.SHUTDOWN, t, text)

        return ContractResult(Intent.UNKNOWN, t, text)


# =========================
# RESPONSE DISPATCHER (NEW CRITICAL FIX)
# =========================
class ContractDispatcher:

    @staticmethod
    def respond(contract: ContractResult) -> str:

        if contract.intent == Intent.TIME:
            now = datetime.now().strftime("%H:%M")
            return f"The time is {now}."

        if contract.intent == Intent.DATE:
            today = datetime.now().strftime("%A %B %d, %Y")
            return f"Today is {today}."

        if contract.intent == Intent.JOKE:
            jokes = [
                "Why did the AI cross the road? To optimize the reward function.",
                "I told my CPU a joke... it froze.",
                "Debugging: being the detective in a crime movie where you are also the murderer."
            ]
            return random.choice(jokes)

        if contract.intent == Intent.WAKE:
            return "Yes?"

        if contract.intent == Intent.SHUTDOWN:
            return "Shutting down."

        return ""