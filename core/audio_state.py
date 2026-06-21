import time
import threading


class AudioState:
    """
    Deterministic audio state machine for:
    - VAD gating
    - TTS suppression
    - echo prevention
    """

    def __init__(self):
        self._lock = threading.Lock()

        self.is_speaking = False
        self.mute_until = 0
        self.cooldown_until = 0

    # -------------------------
    # INTERNAL TIME CHECK
    # -------------------------
    def _now(self):
        return time.time()

    # -------------------------
    # TTS START
    # -------------------------
    def start_speaking(self, hold_seconds=1.5):
        with self._lock:
            now = self._now()

            self.is_speaking = True
            self.mute_until = now + hold_seconds

    # -------------------------
    # TTS END
    # -------------------------
    def stop_speaking(self, cooldown=0.8):
        with self._lock:
            now = self._now()

            self.is_speaking = False
            self.cooldown_until = now + cooldown

    # -------------------------
    # MIC GATE CHECK (MAIN FIX HERE)
    # -------------------------
    def mic_allowed(self) -> bool:
        now = self._now()

        # hard block during speaking
        if self.is_speaking:
            return False

        # block during TTS buffer window
        if now < self.mute_until:
            return False

        # block during post-TTS cooldown
        if now < self.cooldown_until:
            return False

        return True

    # -------------------------
    # DEBUG HELP (VERY USEFUL)
    # -------------------------
    def debug(self):
        return {
            "is_speaking": self.is_speaking,
            "mute_left": max(0, self.mute_until - self._now()),
            "cooldown_left": max(0, self.cooldown_until - self._now()),
            "mic_allowed": self.mic_allowed()
        }


audio_state = AudioState()