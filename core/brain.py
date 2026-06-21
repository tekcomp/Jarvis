# ==============================
# core/brain.py (CONTRACT STABLE LAYER v3)
# ==============================

import datetime

# =========================================================
# INTERNAL STATE (FOR FUTURE EXPANSION)
# =========================================================
_internal_state = {
    "session_active": True
}


# =========================================================
# RESET HOOK (CI REQUIRED)
# =========================================================
def reset():
    """
    CI lifecycle reset hook.
    Clears transient brain state between tests or sessions.
    """

    global _internal_state

    _internal_state = {
        "session_active": True
    }

    print("[BRAIN] RESET COMPLETE")


# =========================================================
# CORE RESPONSE ENGINE
# =========================================================
def generate_response(text: str) -> str:

    t = text.lower().strip()

    if "time" in t:
        now = datetime.datetime.now().strftime("%H:%M:%S")
        return f"The time is {now}."

    if "date" in t or "today" in t:
        today = datetime.datetime.now().strftime("%A, %B %d, %Y")
        return f"Today is {today}."

    if "joke" in t:
        return "Why did the AI cross the road? To optimize the reward function."

    return f"You said: {text}"


# =========================================================
# STREAMING WRAPPER (CI / TTS)
# =========================================================
def stream_response(text: str):

    response = generate_response(text)

    for token in response.split():
        yield token + " "


# =========================================================
# CI ENTRYPOINT
# =========================================================
def handle(text: str) -> str:
    """
    CI synchronous entrypoint.
    """

    return generate_response(text)