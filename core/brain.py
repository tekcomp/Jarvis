import re
from datetime import datetime

def clean(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^\w\s]", "", text)
    return text.strip()

def handle(text: str) -> str:
    text = clean(text)

    # remove wake words
    text = text.replace("hey jarvis", "")
    text = text.replace("jarvis", "")
    text = text.strip()

    # wake word only
    if text == "":
        return "Yes sir."

    # greetings
    if "hello" in text:
        return "Hello sir."

    if "good morning" in text:
        return "Good morning sir."

    if "good afternoon" in text:
        return "Good afternoon sir."

    if "good evening" in text:
        return "Good evening sir."

    # identity
    if "your name" in text:
        return "I am Jarvis."

    # time
    if "time" in text:
        return f"The time is {datetime.now().strftime('%I:%M %p')}."

    # joke
    if "joke" in text:
        return "Why did the AI go to school? To improve its neural network."

    # math test
    if "2 plus 2" in text:
        return "2 plus 2 equals 4."

    return "I did not understand that command."
