import speech_recognition as sr

def listen_and_transcribe():
    recognizer = sr.Recognizer()
    microphone = sr.Microphone()

    with microphone as source:
        print("Listening...")
        audio_data = recognizer.listen(source)

    try:
        text = recognizer.recognize_google(audio_data).strip().lower()
        print(f"Recognized: {text}")
    except sr.UnknownValueError:
        print("Google Speech Recognition could not understand the audio")
    except sr.RequestError as e:
        print(f"Could not request results from Google Speech Recognition service; {e}")

if __name__ == "__main__":
    listen_and_transcribe()