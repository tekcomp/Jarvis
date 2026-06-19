from llm.ollama import ask_ai
from tts.voice import speak

WAKE_WORD = "jarvis"

NOISE_INPUTS = {
    "you",
    "thanks for watching",
    "hmm",
    "uh",
    "ok",
    ""
}


def handle(text: str, qa_mode: bool = False) -> str:
    if not text:
        return ""

    text = text.strip().lower()

    if len(text) < 2:
        return ""

    # --------------------------
    # MODE 1: QA MODE (STRICT)
    # --------------------------
    if qa_mode:
        prompt = text

    # --------------------------
    # MODE 2: VOICE MODE
    # --------------------------
    else:
        if WAKE_WORD not in text:
            return ""

        prompt = text.replace(WAKE_WORD, "").strip()

    # --------------------------
    # NOISE FILTER (CRITICAL)
    # --------------------------
    if prompt in NOISE_INPUTS:
        return ""

    try:
        response = ask_ai(
            "You are Jarvis. Respond in 1–2 short sentences.\n\n"
            f"User: {prompt}"
        )
    except Exception as e:
        return f"error: {e}"

    response = str(response).strip() if response else ""

    if not qa_mode:
        speak(response)

    return response