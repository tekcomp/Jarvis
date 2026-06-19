from llm.ollama import ask_ai
from tts.voice import speak

WAKE_WORD = "jarvis"

def handle(text: str):
    if not text:
        return ""

    text = text.strip().lower()

    print("Heard:", text)

    # -------------------------
    # CASE 1: WAKE WORD PRESENT
    # -------------------------
    if WAKE_WORD in text:
        prompt = text.replace(WAKE_WORD, "").strip()

        if not prompt:
            prompt = "Yes?"

        response = ask_ai(
            "You are Jarvis. Be helpful, concise.\n\nUser: " + prompt
        )

        print("Jarvis:", response)
        speak(response)
        return response

    # -------------------------
    # CASE 2: DIRECT QUESTION MODE (NO WAKE WORD)
    # -------------------------
    # THIS FIXES YOUR PROBLEM
    response = ask_ai(
        "You are Jarvis. Answer concisely.\n\nUser: " + text
    )

    print("Jarvis:", response)
    speak(response)
    return response