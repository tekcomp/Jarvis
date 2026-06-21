from datetime import datetime
from core.memory import add
from core.interruption import is_interrupted


WAKE_WORD = "jarvis"
active = False


# =========================================================
# STREAMING RESPONSE GENERATOR
# =========================================================
def stream_response(text: str):
    """
    Yields partial response chunks (simulates LLM streaming)
    """

    text = text.lower().strip()

    if not text:
        return

    add("user", text)

    # ---------------- TIME ----------------
    if "time" in text:
        now = datetime.now().strftime("%H:%M")
        yield "The time is"
        if is_interrupted(): return
        yield f" {now}."
        return

    # ---------------- DATE ----------------
    if "date" in text or "today" in text:
        today = datetime.now().strftime("%A %B %d")
        yield "Today is"
        if is_interrupted(): return
        yield f" {today}."
        return

    # ---------------- JOKE ----------------
    if "joke" in text:
        yield "Why did the AI cross the road?"
        if is_interrupted(): return
        yield " To optimize the reward function."
        return

    # ---------------- FALLBACK ----------------
    yield "I didn't understand that clearly."