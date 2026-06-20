from core.router import route
import re


def clean(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^\w\s]", "", text)
    return text.strip()


def handle(text: str) -> str:
    text = clean(text)
    return route(text)