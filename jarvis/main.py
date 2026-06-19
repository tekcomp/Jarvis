from stt.vad import get_speech_frames
from stt.whisper import transcribe
from core.brain import handle

print("Jarvis ONLINE (Voice Mode Stable)")

last_text = ""


def main():
    global last_text

    for audio_chunk in get_speech_frames():

        text = transcribe(audio_chunk)

        if not text:
            continue

        text = text.strip().lower()

        # dedupe repeated STT
        if text == last_text:
            continue

        last_text = text

        print("\nHeard:", text)

        response = handle(text)

        if response:
            print("Jarvis:", response)


if __name__ == "__main__":
    main()