from stt.whisper import transcribe
from llm.ollama import stream
from tts.voice import speak
import state
import config


def handle(buffer):
    text = transcribe(buffer)

    if not text:
        return

    print("Heard:", text)

    if "stop" in text:
        state.state.stop_speaking = True
        return

    if any(w in text.lower() for w in config.WAKE_WORDS):
        speak("Yes?")
        return

    reply = ""

    for token in stream(text):
        reply += token

        if token.endswith(".") or token.endswith(","):
            speak(reply)
            reply = ""

    if reply:
        speak(reply)