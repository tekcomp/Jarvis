from datetime import datetime
from core.memory import add
from core.interruption import is_interrupted


WAKE_WORD = "jarvis"
active = False


# =========================================================
# INTENT NORMALIZER (FIXES WEAK WHISPER PHRASES)
# =========================================================
def normalize(text: str) -> str:
    text = text.lower().strip()

    # handle weak / incomplete speech
    if "can you" in text:
        return "what can you do"

    if "what can" in text:
        return "what can you do"

    if "show me" in text and "demo" in text:
        return "demo"

    if text in ["can you do", "what can you", "demo please"]:
        return "demo"

    return text


# =========================================================
# STREAMING RESPONSE ENGINE
# =========================================================
def stream_response(text: str):
    """
    Streaming response generator (Alive Brain v3.1 stable)
    """

    text = normalize(text)

    if not text:
        return

    add("user", text)

    # =====================================================
    # TIME INTENT
    # =====================================================
    if "time" in text:
        now = datetime.now().strftime("%H:%M")

        yield "The time is"
        if is_interrupted():
            return
        yield f" {now}."
        return

    # =====================================================
    # DATE INTENT
    # =====================================================
    if "date" in text or "today" in text:
        today = datetime.now().strftime("%A %B %d")

        yield "Today is"
        if is_interrupted():
            return
        yield f" {today}."
        return

    # =====================================================
    # JOKE INTENT
    # =====================================================
    if "joke" in text:

        yield "Why did the AI cross the road?"
        if is_interrupted():
            return
        yield " To optimize the reward function."
        return

    # =====================================================
    # CAPABILITY / DEMO INTENT
    # =====================================================
    if "what can you do" in text or "demo" in text:

        yield "I can process speech, stream responses, and respond in real time."
        return

    # =====================================================
    # FALLBACK
    # =====================================================
    yield "I didn't understand that clearly."


# =========================================================
# CI COMPATIBILITY LAYER (IMPORTANT)
# =========================================================
def handle(text: str) -> str:
    """
    Non-streaming wrapper for CI + legacy pipeline
    """

    if not text:
        return ""

    chunks = []

    for part in stream_response(text):
        if is_interrupted():
            break
        chunks.append(part)

    return "".join(chunks)

# =========================================================
# TESTING UTILS
# =========================================================
def reset():
    """
    CI compatibility hook.
    Resets conversational state safely.
    """

    global active
    try:
        active = False
    except:
        pass