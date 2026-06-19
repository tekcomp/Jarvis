from llm.ollama import ask_ai
from tts.voice import speak

# -------------------------
# BRAIN HANDLER (MAIN LOGIC)
# -------------------------

def handle(text: str):
    """
    Main brain entry point.
    Receives FINAL transcribed text ONLY (never audio).
    """

    print("DEBUG BRAIN LOADED")

    if not text:
        return

    text = text.strip().lower()

    # -------------------------
    # WAKE WORD CHECK
    # -------------------------
    prompt = text.replace("hey jarvis", "")
    prompt = prompt.replace("jarvis", "")
    prompt = prompt.strip()

    if not prompt:
        speak("Yes?")
        return

    # Optional cleanup: remove wake word for cleaner prompt
    prompt = text.replace("jarvis", "").strip()

    if not prompt:
        prompt = "Yes?"

    # -------------------------
    # CALL LLM (OLLAMA)
    # -------------------------
    response = ask_ai(
        f"You are Jarvis, a helpful AI assistant. "
        f"Respond naturally and concisely.\n\nUser: {prompt}"
    )

    print("Jarvis:", response)

    # -------------------------
    # SPEAK RESPONSE
    # -------------------------
    speak(response)