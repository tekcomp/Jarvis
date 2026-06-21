import pyttsx3

def speak(text: str):
    print("[TTS TEST] creating engine")

    engine = pyttsx3.init()   # NEW ENGINE EVERY TIME
    engine.setProperty("rate", 180)

    print("[TTS TEST] speaking:", text)

    engine.say(text)
    engine.runAndWait()

    print("[TTS TEST] done")