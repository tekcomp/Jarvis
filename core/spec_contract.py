from dataclasses import dataclass
from enum import Enum


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


class SpecContractV2:

    @staticmethod
    def classify(text: str) -> ContractResult:

        if not text or text.strip() == "":
            return ContractResult(Intent.NOISE, "", text)

        t = text.lower().strip()

        if t == "jarvis":
            return ContractResult(Intent.WAKE, t, text)

        if "what time" in t:
            return ContractResult(Intent.TIME, t, text)

        if "date" in t or "today" in t:
            return ContractResult(Intent.DATE, t, text)

        if "joke" in t:
            return ContractResult(Intent.JOKE, t, text)

        if t in ["bye", "exit", "quit"]:
            return ContractResult(Intent.SHUTDOWN, t, text)

        return ContractResult(Intent.NOISE, "", text)