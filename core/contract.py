# ==============================
# core/contract.py (COGNITIVE CONTRACT CORE v1)
# ==============================

from core.brain import generate_response, stream_response, reset as brain_reset


# =========================================================
# CI SAFE ENTRYPOINT (SYNC)
# =========================================================
def handle(text: str) -> str:
    """
    CI + tests ONLY use this.
    Stable deterministic interface.
    """

    if not text:
        return ""

    return generate_response(text)


# =========================================================
# CI LIFECYCLE RESET
# =========================================================
def reset():
    """
    Resets all transient cognitive state.
    Safe no-op for now, extensible later.
    """

    try:
        brain_reset()
    except Exception:
        pass


# =========================================================
# STREAMING INTERFACE (RUNTIME ONLY)
# =========================================================
def stream(text: str):
    """
    Runtime streaming interface.
    CI tests SHOULD NOT use this directly.
    """

    return stream_response(text)