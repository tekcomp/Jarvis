# ==============================
# core/contract.py (OR wherever CI-FALLBACK exists)

from core.personality_engine_v2 import PersonalityEngineV2
from core.brain import route_intent

personality = PersonalityEngineV2()

# =========================================================
# PUBLIC API (ONLY THING TESTS SEE)
# =========================================================

# =========================================================
# CI SAFE ENTRYPOINT (SYNC)
# =========================================================
def handle(text: str):

    # -----------------------------
    # 1. UPDATE PERSONALITY FIRST
    # -----------------------------
    personality.update(text)

    # -----------------------------
    # 2. MODE-AWARE ROUTING
    # -----------------------------
    response = route_intent(text)

    # -----------------------------
    # 3. CRITICAL FIX: NO FALLBACK OVERRIDE
    # -----------------------------
    if response and response.strip():
        return response

    # -----------------------------
    # 4. ONLY NOW USE PERSONALITY FALLBACK
    # -----------------------------
    mode = personality.mode()

    if mode == "playful":
        return "Haha 😄 I'm not sure, but I'm having fun trying!"

    if mode == "jarvis":
        return "I require more information to proceed, sir."

    if mode == "assistant":
        return "I understand. How can I help you?"

    # FINAL SAFETY
    return "I am ready."


# =========================================================
# CI LIFECYCLE RESET
# =========================================================
def reset():
    """
    Resets all transient cognitive state.
    Safe no-op for now, extensible later.
    """

    try:
        personality.reset()
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