# ==============================
# core/audio_state.py (SPEC v1 FIX)
# ==============================

class AudioState:
    def __init__(self):
        self.mic_enabled = True
        self.interrupted = False

    def mic_allowed(self):
        return self.mic_enabled

    def on_interrupt(self):
        self.interrupted = True

    def reset(self):
        self.interrupted = False


# SINGLETON (CRITICAL — fixes import contract)
audio_state = AudioState()