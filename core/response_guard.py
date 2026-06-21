import time


class ResponseGuard:

    def __init__(self):
        self.last_text = ""
        self.last_response = ""
        self.last_time = 0

        self.cooldown_sec = 2.0

    def should_block(self, text: str) -> bool:

        now = time.time()

        # cooldown window
        if now - self.last_time < self.cooldown_sec:
            return True

        # duplicate intent suppression
        if text.strip().lower() == self.last_text.strip().lower():
            return True

        return False

    def update(self, text: str, response: str):

        self.last_text = text
        self.last_response = response
        self.last_time = time.time()