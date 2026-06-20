from stt.vad import get_speech_frames
from stt.whisper import transcribe
from core.brain import handle
from tts.voice import speak
import state
import time

print("Jarvis ONLINE CORE v6 (CLEAN LOOP)")


def is_valid(text: str) -> bool:
    if not text:
        return False

    text = text.strip().lower()

    noise = {
        "thanks for watching",
        "you",
        "hmm",
        "uh",
        "",
        "undefined"
    }

    if len(text) < 2:
        return False

    return text not in noise


def main():
    last = ""
    cooldown_until = 0

    print("LISTENING...")

    for audio in get_speech_frames():

        if state.state.speaking:
            continue

        text = transcribe(audio)

        if not is_valid(text):
            continue

        text = text.strip().lower()

        # cooldown after speech
        if time.time() < cooldown_until:
            continue

        if text == last:
            continue

        last = text

        print("Heard:", text)

        response = handle(text)

        if not response:
            continue

        print("Jarvis:", response)

        speak(response)

        cooldown_until = time.time() + 1.2


if __name__ == "__main__":
    main()