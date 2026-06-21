from dataclasses import dataclass

@dataclass
class PolicyDecision:
    should_speak: bool
    should_use_tools: bool
    priority: int = 1