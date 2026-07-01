WAKE_WORDS = [
    'jarvis',
    'jervis',
    'travis',
    'drivers',
    'driver'
]

def is_wake_word(text):
    text = text.lower()
    return any(w in text for w in WAKE_WORDS)

detect_wake = is_wake_word
