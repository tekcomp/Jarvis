# jarvis_worldcup/voice_service.py
import speech_recognition as sr
import pyttsx3
from .intents import handle_query
from jarvis_worldcup.intents import handle_query
from jarvis_core.logger import log_info


def speak(text: str) -> None:
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

def listen_once() -> str:
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        audio = r.listen(source)
    try:
        return r.recognize_google(audio)
    except Exception:
        return ""

def main_loop():
    speak("Jarvis is ready.")
    speak("World Cup 2026 schedule service is ready.")
    log_info("Jarvis started voice loop.")
    while True:
        query = listen_once()
        log_info(f"User said: {query}")
        if not query:
            speak("Sorry, I didn't catch that.")
            continue
        print(f"User said: {query}")
        if "exit" in query.lower():
            speak("Goodbye.")
            log_info("Jarvis shutting down.")
            break
        response = handle_query(query)
        print(response)
        speak(response)
        log_info(f"Response spoken: {response}")

if __name__ == "__main__":
    main_loop()
