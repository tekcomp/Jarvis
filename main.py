import signal
import sys
from datetime import datetime

from stt.vad import get_speech_frames, pa, stream
from stt.whisper import transcribe
from core.brain import handle
from tts.voice import speak
import state


# ----------------------------
# DEBUG MODE
# ----------------------------
DEBUG = True


def log(tag, msg):
    if DEBUG:
        time = datetime.now().strftime("%H:%M:%S")
        print(f"[{time}] {tag}: {msg}")


# ----------------------------
# CLEAN SHUTDOWN
# ----------------------------
def shutdown(sig=None, frame=None):
    print("\n[SYS] Shutting down Jarvis safely...")

    try:
        state.state.speaking = False
        stream.stop_stream()
        stream.close()
        pa.terminate()
    except:
        pass

    sys.exit(0)


signal.signal(signal.SIGINT, shutdown)
signal.signal(signal.SIGTERM, shutdown)


# ----------------------------
# FILTER
# ----------------------------
def is_valid(text: str) -> bool:
    if not text:
        return False

    text = text.strip().lower()

    if len(text) < 2:
        return False

    noise = {
        "thanks for watching",
        "thank you for watching",
        "...",
        "undefined"
    }

    return text not in noise


# ----------------------------
# MAIN LOOP
# ----------------------------
def main():

    last_text = ""

    log("SYSTEM", "Jarvis Debug Mode Started")

    for audio in get_speech_frames():

        try:

            # ------------------------
            # WHISPER STAGE
            # ------------------------
            text = transcribe(audio)
            log("WHISPER", text)

            if not is_valid(text):
                log("FILTER", "Rejected noise")
                continue

            text = text.strip().lower()

            if text == last_text:
                log("FILTER", "Duplicate ignored")
                continue

            if state.state.speaking:
                log("STATE", "Speaking active - skipping")
                continue

            last_text = text

            # ------------------------
            # WAKE FILTER
            # ------------------------
            if "jarvis" not in text and "hey" not in text:
                log("WAKE", f"Ignored: {text}")
                continue

            log("INPUT", text)

            # ------------------------
            # BRAIN
            # ------------------------
            response = handle(text)

            if not response:
                response = "I didn't understand that."

            log("JARVIS", response)

            # ------------------------
            # TTS
            # ------------------------
            state.state.speaking = True
            speak(response)
            state.state.speaking = False

        except Exception as e:
            log("ERROR", str(e))


if __name__ == "__main__":
    main()