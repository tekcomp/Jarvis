from datetime import datetime


def cmd_time(text):
    return f"The time is {datetime.now().strftime('%H:%M')}."


def cmd_date(text):
    return f"Today is {datetime.now().strftime('%A %B %d')}."


def cmd_joke(text):
    return "Why did the AI cross the road? To optimize the reward function."


def cmd_capital(text):
    if "florida" in text:
        return "The capital of Florida is Tallahassee."
    return "I don't know that capital yet."

def cmd_hello(text):
    return "Hello sir, I am online."

def cmd_bye(text):
    return "Goodbye sir, have a great day."

def cmd_weather(text):
    return "Weather module not connected yet."

def cmd_news(text):
    import requests
    return requests.get("https://newsapi.org/...").json()

def cmd_fallback(text):
    return "I didn't understand that."