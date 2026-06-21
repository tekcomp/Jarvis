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

        # -------------------------
        # WAKE WORD (HIGHEST PRIORITY)
        # -------------------------
        if t == "jarvis":
            return ContractResult(Intent.WAKE, t, text)

        # -------------------------
        # SHUTDOWN (STRICT MATCH ONLY)
        # -------------------------
        if t in ["bye", "exit", "quit", "shutdown"]:
            return ContractResult(Intent.SHUTDOWN, t, text)

        # -------------------------
        # TIME (STRICT + EXPANDED)
        # -------------------------
        time_keywords = [
            "what time",
            "current time",
            "tell me the time",
            "time is it",
            "what's the time"
        ]

        if any(k in t for k in time_keywords):
            return ContractResult(Intent.TIME, t, text)

        # -------------------------
        # DATE (FIXED LOGIC)
        # -------------------------
        date_keywords = [
            "what is the date",
            "today's date",
            "current date",
            "what date",
            "date today"
        ]

        if any(k in t for k in date_keywords):
            return ContractResult(Intent.DATE, t, text)

        # fallback ONLY if explicit "date" and NOT time query
        if "date" in t and "time" not in t:
            return ContractResult(Intent.DATE, t, text)

        # -------------------------
        # JOKE
        # -------------------------
        if "joke" in t:
            return ContractResult(Intent.JOKE, t, text)

        return ContractResult(Intent.NOISE, "", text)