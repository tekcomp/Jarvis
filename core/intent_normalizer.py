# ==============================
# core/intent_normalizer.py
# ==============================

import re

class IntentNormalizer:

    def __init__(self):
        self.last_intent = None
        self.last_ts = 0

    def normalize(self, text: str) -> str:

        text = text.lower().strip()

        # remove punctuation noise
        text = re.sub(r"[^\w\s]", "", text)

        # collapse whitespace
        text = re.sub(r"\s+", " ", text)

        return text

    def is_duplicate(self, text: str, window_sec: float = 4.0) -> bool:

        import time

        now = time.time()
        norm = self.normalize(text)

        if self.last_intent == norm and (now - self.last_ts) < window_sec:
            return True

        self.last_intent = norm
        self.last_ts = now

        return False