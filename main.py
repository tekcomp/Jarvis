from stt.vad import get_speech_frames
from stt.whisper import transcribe
from core.brain import handle
from tts.voice import speak
import state
import time
import re

print("Jarvis ONLINE CORE v9 (SEMANTIC STABILIZER)")
print("LISTENING...")


# -----------------------------
# CLEAN INPUT
# -----------------------------
def clean(text: str) -> str:
    text = text.lower()
    text = re.sub(r"\bjarvis\b", "", text)
    text = re.sub(r"[^\w\s]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


# -----------------------------
# SEMANTIC NORMALIZER
# -----------------------------
def normalize(text: str) -> str:
    text = clean(text)

    # reduce semantic duplicates
    replacements = {
        "what is the time": "time",
        "what time is it": "time",
        "tell me a joke": "joke",
        "give me a joke": "joke",
        "hello": "hello",
    }

    return replacements.get(text, text)


# -----------------------------
# FILTER
# -----------------------------
def is_valid(text: str) -> bool:
    if not text:
        return False
    if len(text) < 2:
        return False
    return True


# -----------------------------
# MAIN LOOP
# -----------------------------
def main():

    last_intent = ""
    last_time = 0
    COOLDOWN = 2.0

    for audio in get_speech_frames():

        try:
            text = transcribe(audio)

            if not is_valid(text):
                continue

            print("Heard:", text)

            cleaned = normalize(text)

            # -----------------------------
            # WAKE CHECK
            # -----------------------------
            if "jarvis" not in text.lower():
                continue

            # -----------------------------
            # COOLDOWN (anti double trigger)
            # -----------------------------
            now = time.time()
            if now - last_time < COOLDOWN:
                continue

            last_time = now

            # -----------------------------
            # SEMANTIC DEDUP
            # -----------------------------
            intent = cleaned

            if intent == last_intent:
                continue

            last_intent = intent

            print("COMMAND:", intent)

            response = handle(intent)

            if not response:
                continue

            print("Jarvis:", response)

            state.state.speaking = True
            speak(response)
            state.state.speaking = False

        except Exception as e:
            print("[ERROR]", e)


if __name__ == "__main__":
    main()