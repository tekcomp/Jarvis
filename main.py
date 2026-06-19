from stt.vad import get_speech_frames
from stt.whisper import transcribe
from core.brain import handle

print("Jarvis ONLINE v2 (ChatGPT Voice Architecture)")

def main():
    last_text = ""

    while True:
        for audio in get_speech_frames():
            text = transcribe(audio)

            if not text:
                continue

        text = str(text).strip().lower()

        if text == "":
            continue

        if text == last_text:
            continue

        last_text = text

        print("Heard:", text)

        handle(text)


if __name__ == "__main__":
    main()
