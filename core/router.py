NOISE = {"you", "thanks for watching", "hmm", "uh", "ok", ""}

WAKE_WORD = "jarvis"


def should_respond(text: str, mode: str):
    text = text.strip().lower()

    if len(text) < 2:
        return False, ""

    if mode == "voice":
        if WAKE_WORD not in text:
            return False, ""

        text = text.replace(WAKE_WORD, "").strip()

    if text in NOISE:
        return False, ""

    return True, text