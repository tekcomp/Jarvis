from datetime import datetime
from core.memory import add
from core.interruption import is_interrupted
import hashlib

# ✅ SINGLE SOURCE OF TRUTH
from core.spec_contract import SpecContractV2, Intent


WAKE_WORD = "jarvis"
active = False


# =========================================================
# STREAMING RESPONSE ENGINE
# =========================================================
def stream_response(text: str):
    """
    Streaming response generator (contract-driven)
    """

    # -------------------------
    # CONTRACT CLASSIFICATION
    # -------------------------
    result = SpecContractV2.classify(text)
    intent = result.intent

    # store normalized input in memory
    if result.normalized:
        add("user", result.normalized)

    # =====================================================
    # TIME INTENT
    # =====================================================
    if intent == Intent.TIME:
        now = datetime.now().strftime("%H:%M")

        yield "The time is"
        if is_interrupted():
            return
        yield f" {now}."
        return

    # =====================================================
    # DATE INTENT
    # =====================================================
    if intent == Intent.DATE:
        today = datetime.now().strftime("%A %B %d")

        yield "Today is"
        if is_interrupted():
            return
        yield f" {today}."
        return

    # =====================================================
    # JOKE INTENT
    # =====================================================
    if intent == Intent.JOKE:

        yield "Why did the AI cross the road?"
        if is_interrupted():
            return
        yield " To optimize the reward function."
        return

    # =====================================================
    # WAKE INTENT
    # =====================================================
    if intent == Intent.WAKE:
        yield "Yes?"
        return

    # =====================================================
    # NOISE INTENT (IMPORTANT FIX)
    # =====================================================
    if intent == Intent.NOISE:
        yield ""
        return

    # =====================================================
    # SHUTDOWN INTENT
    # =====================================================
    if intent == Intent.SHUTDOWN:
        yield ""
        return

    # =====================================================
    # FALLBACK (UNKNOWN)
    # =====================================================
    yield "I didn't understand that clearly."


# =========================================================
# CI COMPATIBILITY LAYER (NON-STREAMING)
# =========================================================
def handle(text: str) -> str:

    if not text:
        return ""

    result = SpecContractV2.classify(text)
    intent = result.intent

    # -------------------------
    # WAKE WORD HARD OVERRIDE
    # -------------------------
    if intent == Intent.WAKE:
        return "Yes?"

    # -------------------------
    # STREAM EXECUTION
    # -------------------------
    chunks = []

    for part in stream_response(text):
        if is_interrupted():
            break
        chunks.append(part)

    output = "".join(chunks).strip()

    # -------------------------
    # CI SAFE OUTPUT NORMALIZATION
    # -------------------------
    if intent == Intent.NOISE:
        return ""

    if intent == Intent.UNKNOWN and output == "":
        return "I didn't understand that clearly."

    return output


# =========================================================
# LEGACY / FALLBACK ROUTER (UNCHANGED BUT SAFE)
# =========================================================
def brain_handle(input_text: str):

    key = input_text.strip().lower()

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
    global active
    active = False