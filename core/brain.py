from llm.ollama import ask_ai

WAKE_WORD = "jarvis"

NOISE_INPUTS = {"you", "thanks for watching", "hmm", "ok", ""}


def handle(text: str, qa_mode: bool = False) -> str:
    if not text:
        return ""

    text = text.strip().lower()

    if len(text) < 2:
        return ""

    # -----------------------------
    # MODE SWITCH (CRITICAL FIX)
    # -----------------------------
    if not qa_mode:
        if WAKE_WORD not in text:
            return ""

        text = text.replace(WAKE_WORD, "").strip()

    prompt = text

    if prompt in NOISE_INPUTS:
        return ""

    try:
        response = ask_ai(
            "You are Jarvis. Be concise.\n\n"
            f"User: {prompt}"
        )
    except Exception as e:
        return f"error: {e}"

    return str(response).strip() if response else ""