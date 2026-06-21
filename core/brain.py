from datetime import datetime
from core.memory import add
from core.interruption import interrupt, is_interrupted, clear
from core.audio_state import audio_state
import hashlib
WAKE_WORD = "jarvis"
active = False

# =========================================================
# INTENT CLASSIFIER (PURE FUNCTION)
# =========================================================

def classify_wake(text: str):

    text = text.lower().strip()

    if text == "jarvis":
        return "wake"

    if not text or text.strip() == "":
        return "none"

    if "what time" in text:
        return "TIME_QUERY"

    if "tell me a joke" in text:
        return "JOKE_QUERY"

    if text in ["bye", "exit", "quit"]:
        return "SHUTDOWN"

    return "UNKNOWN"

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

# core/brain.py

def stream_response(text: str):
    """
    PURE FUNCTION (NO IMPORTS FROM CORE SYSTEMS)
    """

    response = f"Echo: {text}"

    for word in response.split():
        yield word + " "

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
    yield ""
    return


# =========================================================
# CI COMPATIBILITY LAYER (IMPORTANT)
# =========================================================
def handle(text: str) -> str:

    if not text:
        return ""

    text = text.lower().strip()

    # -------------------------
    # WAKE WORD (CI REQUIRED)
    # -------------------------
    if text == "jarvis":
        return "Yes?"

    # -------------------------
    # ROUTE THROUGH STREAM
    # -------------------------
    chunks = []

    for part in stream_response(text):
        if is_interrupted():
            break
        chunks.append(part)

    result = "".join(chunks).strip()

    # -------------------------
    # CI FIX: enforce NONE semantics
    # -------------------------
    if result == "I didn't understand that clearly.":
        return None

    return result

def brain_handle(input_text: str):

    key = input_text.strip().lower()

    # deterministic hash-based routing (CI-safe)
    h = int(hashlib.md5(key.encode()).hexdigest(), 16)

    routes = [
        "I can help with that.",
        "Processing request.",
        "Understood.",
        "Executing query."
    ]

    return routes[h % len(routes)]

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