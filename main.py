from stt.vad import get_speech_frames
from stt.whisper import transcribe
from core.brain import handle
from tts.voice import speak
import state

print("Jarvis ONLINE CORE v12 (CLEAN FULL REPLACE)")

# ----------------------------
# STATE
# ----------------------------
last_text = ""


# ----------------------------
# FILTER
# ----------------------------
NOISE = {
    "thank you",
    "thanks",
    "thanks for watching",
    "bye",
    "ok",
    "okay",
    "",
    " "
}


def is_noise(text: str) -> bool:
    text = text.strip().lower()
    return text in NOISE


def is_command(text: str) -> bool:
    t = text.lower()
    return (
        "jarvis" in t or
        "hey" in t or
        "what" in t or
        "how" in t or
        "tell me" in t
    )


def clean_command(text: str) -> str:
    text = text.lower()
    text = text.replace("jarvis", "")
    text = text.replace("hey", "")
    text = text.strip()

    if len(text) < 2:
        return ""

    return text


# ----------------------------
# MAIN LOOP
# ----------------------------
def main():

    global last_text

    print("LISTENING...")

    for audio in get_speech_frames():

        text = transcribe(audio)

        if not text:
            continue

        if is_noise(text):
            continue

        text = text.strip().lower()

        if text == last_text:
            continue

        last_text = text

        print("Heard:", text)

        # ----------------------------
        # INTENT GATE
        # ----------------------------
        if not is_command(text):
            continue

        command = clean_command(text)

        if not command:
            continue

        print("COMMAND:", command)

        response = handle(command)

        if not response:
            continue

        print("Jarvis:", response)

        state.state.speaking = True
        speak(response)
        state.state.speaking = False


if __name__ == "__main__":
    main()