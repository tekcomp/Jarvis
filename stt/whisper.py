import speech_recognition as sr

from core.logger import L3, LOG_LEVEL
from core.duplex_guard import duplex

def transcribe(audio):
    recognizer = sr.Recognizer()
    
    if duplex.muted():
        return ""

    try:
        with sr.AudioFile(audio) as source:
            audio_data = recognizer.record(source)
            text = recognizer.recognize_google(audio_data).strip().lower()
    except sr.UnknownValueError:
        L3("SPEECH RECOGNITION EMPTY RESULT")
        return ""
    except sr.RequestError as e:
        L3(f"SPEECH RECOGNITION ERROR: {e}")
        return ""

    if not text:
        L3("SPEECH RECOGNITION EMPTY RESULT")
        return ""

    if LOG_LEVEL >= 3:
        L3(f"RECOGNIZED TEXT: {text}")

    return text