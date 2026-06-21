# core/audio_state.py

class AudioState:
    def __init__(self):
        self._speaking = False
        self.request_interrupt = False

    def start_speaking(self, hold_seconds=1.2):
        self._speaking = True

    def stop_speaking(self):
        self._speaking = False

    def on_interrupt(self):
        # no dependency on interruption module
        self.request_interrupt = True


audio_state = AudioState()