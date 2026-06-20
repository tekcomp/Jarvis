from stt.vad import get_speech_frames
from stt.whisper import transcribe
from core.brain import handle
from tts.voice import speak
import state

print("Jarvis ONLINE (STABLE LOOP V4)")

# ----------------------------
# LOCAL SAFETY STATE
# ----------------------------
last_text = ""
system_lock = False   # prevents echo loops


def is_valid(text: str) -> bool:
    if not text:
        return False

    text = text.strip().lower()

    if len(text) < 2:
        return False

    noise = {
        "you", "uh", "hmm", "thanks for watching",
        " ", "...", "undefined"
    }

    return text not in noise


# ----------------------------
# MAIN LOOP
# ----------------------------
def main():

    global last_text, system_lock

    print("VAD LOOP STARTED (LISTENING...)")

    for audio in get_speech_frames():

        try:
            text = transcribe(audio)

            if not is_valid(text):
                continue

            text = text.strip().lower()

            # 🔒 prevent duplicate triggers
            if text == last_text:
                continue

            # 🔒 prevent self echo
            if state.state.speaking:
                continue

            last_text = text

            print("Heard:", text)

            # ----------------------------
            # WAKE FILTER (optional safety)
            # ----------------------------
            if "jarvis" not in text and "hey" not in text:
                continue

            # ----------------------------
            # PROCESS BRAIN
            # ----------------------------
            response = handle(text)

            if not response:
                response = "I didn't understand that."

            print("Jarvis:", response)

            # ----------------------------
            # SPEAK (LOCKED)
            # ----------------------------
            state.state.speaking = True
            speak(response)

            # give TTS time to finish (prevents echo loop)
            state.state.speaking = False

        except Exception as e:
            print("[MAIN LOOP ERROR]", e)


# ----------------------------
# ENTRY POINT
# ----------------------------
if __name__ == "__main__":
    main()