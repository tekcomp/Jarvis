from stt.vad import get_speech_frames
from stt.whisper import transcribe
from core.brain import handle
from tts.voice import speak
import state
from datetime import datetime

print("Jarvis ONLINE CORE (STABLE V17.2 CLEAN REBUILD)")


# ----------------------------
# CLEAN TEXT UTILITIES
# ----------------------------

def clean_text(text: str) -> str:
    if not text:
        return ""

    text = text.lower().strip()

    # remove wake word early (CRITICAL FIX)
    text = text.replace("jarvis", "")
    text = text.replace("hey", "")
    text = text.replace(",", " ")

    # normalize spacing
    text = " ".join(text.split())

    return text


def is_valid(text: str) -> bool:
    if not text:
        return False

    text = text.strip()

    if len(text) < 4:
        return False

    # reject garbage fragments
    junk = [
        "thanks for watching",
        "thank you very much",
        "the time is",
        "i see a couple",
        "music",
        "applause"
    ]

    t = text.lower()
    for j in junk:
        if j in t:
            return False

    # reject ultra-fragmented speech
    if len(text.split()) < 2:
        return False

    return True


def safe_handle(text: str) -> str:
    """
    Brain wrapper with full safety protection
    """
    try:
        if not text:
            return "I didn't hear anything clearly."

        return handle(text)

    except Exception as e:
        print("[MAIN ERROR]", e)
        return "I couldn't process that request."


# ----------------------------
# MAIN LOOP
# ----------------------------

def main():

    last_text = ""

    print("LISTENING...")

    for audio in get_speech_frames():

        try:

            text = transcribe(audio)

            if not is_valid(text):
                continue

            text = clean_text(text)

            if not text:
                continue

            # prevent duplicate execution
            if text == last_text:
                continue

            last_text = text

            print("Heard:", text)

            # ----------------------------
            # ROUTING DECISION LAYER
            # ----------------------------

            # wake-only filtering
            if len(text) < 2:
                continue

            # ----------------------------
            # EXECUTE BRAIN
            # ----------------------------

            response = safe_handle(text)

            if not response:
                response = "I didn't understand that."

            print("Jarvis:", response)

            # ----------------------------
            # SPEAK SAFETY LOCK
            # ----------------------------

            state.state.speaking = True
            speak(response)
            state.state.speaking = False

        except Exception as e:
            print("[LOOP ERROR]", e)


# ----------------------------
# ENTRY POINT
# ----------------------------

if __name__ == "__main__":
    main()