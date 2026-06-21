import time

class AudioState:

    def __init__(self):
        self.is_speaking = False
        self.mute_until = 0
        self.cooldown_until = 0

    # -------------------------
    # TTS START
    # -------------------------
    def start_speaking(self, hold_seconds=1.5):
        self.is_speaking = True
        self.mute_until = time.time() + hold_seconds

    # -------------------------
    # TTS END
    # -------------------------
    def stop_speaking(self, cooldown=0.8):
        self.is_speaking = False
        self.cooldown_until = time.time() + cooldown

    # -------------------------
    # MIC GATE CHECK
    # -------------------------
    def mic_allowed(self) -> bool:
        now = time.time()

        if self.is_speaking:
            return False

        if now < self.mute_until:
            return False

        if now < self.cooldown_until:
            return False

        return True


audio_state = AudioState()