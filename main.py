from stt.vad import get_speech_frames
from stt.whisper import transcribe
from core.brain import handle
import state

print("Jarvis ONLINE v2 (ChatGPT Voice Architecture)")


def main():
    for audio in get_speech_frames():

        text = transcribe(audio)

        if not text:
            continue

        text = text.strip().lower()

        if text == state.state.last_user_text:
            continue

        state.state.last_user_text = text

        print("Heard:", text)

        handle(text)
        
last_text = ""

def is_noise(text: str):
    noise = {"you", "thanks for watching", "hmm", "uh", ""}
    return text.strip().lower() in noise

for audio_chunk in get_speech_frames():

    text = transcribe(audio_chunk)

    if not text:
        continue

    text = text.strip().lower()

    if is_noise(text):
        continue

    if text == last_text:
        continue

    last_text = text

    handle(text)

if __name__ == "__main__":
    main()