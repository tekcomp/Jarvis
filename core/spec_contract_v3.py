from dataclasses import dataclass
from enum import Enum
from typing import Optional, Any, Dict


# =========================================================
# VERSIONED INTENT SYSTEM
# =========================================================

class Intent(str, Enum):
    TIME = "time"
    DATE = "date"
    JOKE = "joke"
    WAKE = "wake"
    SHUTDOWN = "shutdown"
    NOISE = "none"
    UNKNOWN = "unknown"


# =========================================================
# CONTRACT RESULT (v3 STRICT SCHEMA)
# =========================================================

@dataclass
class ContractResult:
    version: str
    intent: Intent
    normalized: str
    raw: str
    confidence: float = 1.0


# =========================================================
# SCHEMA REGISTRY (VERSION CONTROL)
# =========================================================

SCHEMA_VERSIONS = {
    "v1": ["intent", "raw"],
    "v2": ["intent", "normalized", "raw"],
    "v3": ["version", "intent", "normalized", "raw", "confidence"],
}


# =========================================================
# ENFORCER (THE IMPORTANT PART)
# =========================================================

class SpecContractV3:

    VERSION = "v3"

    @staticmethod
    def enforce(result: Any) -> ContractResult:

        # -----------------------------------------
        # TYPE SAFETY GUARD
        # -----------------------------------------
        if not isinstance(result, ContractResult):
            raise TypeError(f"[SPEC-V3] Invalid contract type: {type(result)}")

        # -----------------------------------------
        # VERSION ENFORCEMENT
        # -----------------------------------------
        if result.version != SpecContractV3.VERSION:
            raise ValueError(
                f"[SPEC-V3] Version mismatch: expected {SpecContractV3.VERSION}, got {result.version}"
            )

        # -----------------------------------------
        # REQUIRED FIELD VALIDATION
        # -----------------------------------------
        missing = []

        for field in SCHEMA_VERSIONS["v3"]:
            if not hasattr(result, field):
                missing.append(field)

        if missing:
            raise ValueError(f"[SPEC-V3] Missing fields: {missing}")

        # -----------------------------------------
        # INTENT VALIDATION
        # -----------------------------------------
        if result.intent is None:
            raise ValueError("[SPEC-V3] Intent cannot be None")

        # -----------------------------------------
        # NORMALIZATION GUARANTEE
        # -----------------------------------------
        if result.normalized is None:
            result.normalized = ""

        # -----------------------------------------
        # CONFIDENCE CLAMP
        # -----------------------------------------
        result.confidence = max(0.0, min(1.0, result.confidence))

        return result


# =========================================================
# BUILDER (SAFE CREATION LAYER)
# =========================================================

class SpecBuilderV3:

    @staticmethod
    def build(intent: Intent, normalized: str, raw: str, confidence: float = 1.0):

        return ContractResult(
            version="v3",
            intent=intent,
            normalized=normalized,
            raw=raw,
            confidence=confidence
        )