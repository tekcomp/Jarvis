from stt.vad import get_speech_frames
from stt.whisper import transcribe
from core.brain import handle
from tts.voice import speak

from core.logger import L3


def main():

    print("[SYSTEM] BOOTING JARVIS CORE")
    print("[SYSTEM] LISTENING...\n")

    for audio in get_speech_frames():

        try:

            L3("AUDIO RECEIVED FROM VAD")

            # -------------------------
            # TRANSCRIBE
            # -------------------------
            text = transcribe(audio)

            if not text:
                L3("WHISPER EMPTY")
                continue

            print(f"[HEARD] {text}")

            # -------------------------
            # INTENT + RESPONSE
            # -------------------------
            response = handle(text)

            if response:
                print(f"[JARVIS] {response}")
                speak(response)

        except Exception as e:
            print(f"[MAIN ERROR] {e}")


if __name__ == "__main__":
    main()