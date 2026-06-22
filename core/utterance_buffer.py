# core/utterance_buffer.py

import time


class UtteranceBuffer:

    def __init__(self):
        self.buffer = ""
        self.last_time = 0
        self.silence_threshold = 1.2  # IMPORTANT FIX (was too low before)

    def add(self, text: str):
        self.buffer += " " + text
        self.last_time = time.time()

    def should_finalize(self) -> bool:
        """
        ONLY finalize when:
        - silence threshold reached
        - AND buffer has meaningful length
        """

        if not self.buffer.strip():
            return False

        silence_time = time.time() - self.last_time

        # 🚨 CRITICAL FIX: prevent early flush
        if silence_time < self.silence_threshold:
            return False

        # require minimum meaningful phrase length
        if len(self.buffer.strip().split()) < 2:
            return False

        return True

    def finalize(self) -> str:
        text = self.buffer
        self.buffer = ""
        return text