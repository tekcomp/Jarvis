import re


class IntentResult:
    def __init__(self, intent, confidence, cleaned):
        self.intent = intent
        self.confidence = confidence
        self.cleaned = cleaned


# ----------------------------
# INTENT DEFINITIONS
# ----------------------------

INTENTS = {
    "time": [
        r"\bwhat time is it\b",
        r"\btell me the time\b",
        r"\bcurrent time\b",
        r"\bwhat is the time\b",
    ],
    "date": [
        r"\bwhat is the date\b",
        r"\btoday'?s date\b",
        r"\bwhat day is it\b",
    ],
    "joke": [
        r"\btell me a joke\b",
        r"\bjoke\b",
        r"\bmake me laugh\b",
    ],
    "weather": [
        r"\bweather\b",
        r"\bwhat is the weather\b",
    ],
}


#----------------------------
# HANDLE QUERY
#----------------------------

def handle_query(text: str) -> str:
    t = text.lower()

    if "show logs" in t or "jarvis logs" in t:
        try:
            with open("logs/jarvis.log", "r") as f:
                last_lines = f.readlines()[-20:]
            return "Here are the latest Jarvis logs:\n" + "".join(last_lines)
        except Exception:
            return "I couldn't access the logs. Make sure the log file exists."

    ...



# ----------------------------
# CLEAN INPUT
# ----------------------------

def normalize(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^\w\s]", "", text)
    return text


# ----------------------------
# CONFIDENCE SCORING ENGINE
# ----------------------------

def score_intent(text: str) -> IntentResult:

    text = normalize(text)

    best_intent = None
    best_score = 0.0

    # base speech quality scoring
    words = text.split()
    base_score = min(len(words) / 6.0, 1.0)  # longer = more reliable

    for intent, patterns in INTENTS.items():
        for p in patterns:
            if re.search(p, text):

                # strong match
                score = 0.85 + base_score * 0.15

                if score > best_score:
                    best_score = score
                    best_intent = intent

    # fallback fuzzy intent detection
    if best_intent is None:

        if "time" in text:
            best_intent = "time"
            best_score = 0.55 + base_score * 0.2

        elif "date" in text or "today" in text:
            best_intent = "date"
            best_score = 0.55 + base_score * 0.2

        elif "joke" in text:
            best_intent = "joke"
            best_score = 0.55 + base_score * 0.2

        elif "weather" in text:
            best_intent = "weather"
            best_score = 0.55 + base_score * 0.2

    return IntentResult(best_intent, best_score, text)