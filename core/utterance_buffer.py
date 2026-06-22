# ==============================
# core/utterance_buffer.py
# STABLE SPEECH COLLAPSE LAYER
# ==============================

import time

class UtteranceBuffer:

    def __init__(self):
        self.buffer = []
        self.last_push = 0
        self.silence_threshold = 1.2  # seconds
        self.final_text = ""

    def add(self, text: str):
        self.buffer.append(text)
        self.last_push = time.time()

    def should_finalize(self) -> bool:
        return (time.time() - self.last_push) > self.silence_threshold

    def finalize(self) -> str:

        if not self.buffer:
            return ""

        # collapse duplicates
        cleaned = " ".join(self.buffer)

        self.buffer = []
        self.final_text = cleaned

        return cleaned