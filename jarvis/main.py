from stt.vad import get_speech_frames
from stt.whisper import transcribe
from core.brain import handle
import state

print("Jarvis ONLINE (REAL Voice Mode)")


def main():
    buffer = []

    for audio_chunk in get_speech_frames():

        text = transcribe(audio_chunk)

        if not text:
            continue

        text = text.strip().lower()

        # dedupe
        if text == state.state.last_text:
            continue

        state.state.last_text = text

        print("Heard:", text)

        # forward immediately
        handle(text)


if __name__ == "__main__":
    main()