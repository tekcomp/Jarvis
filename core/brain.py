import re

def clean(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^\w\s]", "", text)
    return text.strip()


def handle(text: str) -> str:
    text = clean(text)

    if not text:
        return ""

    if "jarvis" in text:
        if "joke" in text:
            return "Why did the AI cross the road? To optimize the reward function."
        if "time" in text:
            from datetime import datetime
            return f"The time is {datetime.now().strftime('%H:%M')}."
        if "hello" in text:
            return "Hello, I am online."

        return "Yes sir."

    return ""