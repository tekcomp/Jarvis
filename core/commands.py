from datetime import datetime
import random

def cmd_time(text):
    return f"The time is {datetime.now().strftime('%H:%M')}."


def cmd_date(text):
    return f"Today is {datetime.now().strftime('%A %B %d')}."


def cmd_joke(text):
    return get_random_dad_joke()

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

def get_random_dad_joke():
    """
    Return one random dad joke from a predefined list.
    Includes basic validation and safe fallback handling.
    """
    dad_jokes = [
        "Why don't eggs tell jokes? They'd crack each other up.",
        "I'm reading a book about anti-gravity. It's impossible to put down!",
        "Why did the scarecrow win an award? Because he was outstanding in his field.",
        "I would avoid the sushi if I was you. It’s a little fishy.",
        "Why did the math book look sad? Because it had too many problems.",
        "I told my computer I needed a break... and now it won’t stop sending me KitKat ads.",
        "Why don't skeletons fight each other? They don't have the guts."
    ]

    # Validate the list is not empty
    if not isinstance(dad_jokes, list) or len(dad_jokes) == 0:
        return "No jokes available right now."

    return random.choice(dad_jokes)


# Example usage (runs safely)
if __name__ == "__main__":
    try:
        print(get_random_dad_joke())
    except Exception as e:
        print(f"An unexpected error occurred: {e}")