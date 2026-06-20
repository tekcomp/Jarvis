import time

class AudioState:
    def __init__(self):
        self.is_speaking = False
        self.speak_until = 0
        self.ignore_until = 0

    def start_speaking(self, duration=2.0):
        self.is_speaking = True
        self.speak_until = time.time() + duration
        self.ignore_until = self.speak_until + 0.5  # buffer

    def stop_speaking(self):
        self.is_speaking = False

    def is_blocked(self):
        return time.time() < self.ignore_until


audio_state = AudioState()