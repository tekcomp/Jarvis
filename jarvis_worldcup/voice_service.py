# jarvis_worldcup/voice_service.py
import speech_recognition as sr
import pyttsx3
from .intents import handle_query

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
    speak("World Cup 2026 schedule service is ready.")
    while True:
        query = listen_once()
        if not query:
            speak("Sorry, I didn't catch that.")
            continue
        print(f"User said: {query}")
        if "exit" in query.lower():
            speak("Goodbye.")
            break
        response = handle_query(query)
        print(response)
        speak(response)

if __name__ == "__main__":
    main_loop()
