from dataclasses import dataclass

@dataclass
class PerceptionEvent:
    text: str
    source: str = "stt"
    confidence: float = 1.0