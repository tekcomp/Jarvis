import time
from core.interruption import interrupt


class Arbitrator:
    """
    Single source of truth for ALL interrupt decisions.
    CI-safe deterministic barge-in controller.
    """

    def __init__(self):
        self.tts_active = False
        self.user_speaking = False

        self._interrupt_fired = False
        self._last_interrupt_time = 0

        self.COOLDOWN = 1.0  # CI-safe debounce

    # =====================================================
    # STATE UPDATES (EVENTS ONLY)
    # =====================================================
    def on_tts_start(self):
        self.tts_active = True
        self._interrupt_fired = False

    def on_tts_end(self):
        self.tts_active = False
        self._interrupt_fired = False

    def on_user_speech_start(self):
        self.user_speaking = True
        self._evaluate_interrupt()

    def on_user_speech_end(self):
        self.user_speaking = False

    # =====================================================
    # CORE DECISION ENGINE
    # =====================================================
    def _evaluate_interrupt(self):

        now = time.time()

        if (
            self.tts_active
            and self.user_speaking
            and not self._interrupt_fired
            and (now - self._last_interrupt_time) > self.COOLDOWN
        ):
            interrupt()

            self._interrupt_fired = True
            self._last_interrupt_time = now

    # =====================================================
    # DEBUG HELP
    # =====================================================
    def state(self):
        return {
            "tts_active": self.tts_active,
            "user_speaking": self.user_speaking,
            "interrupt_fired": self._interrupt_fired,
        }


# GLOBAL SINGLETON
arbitrator = Arbitrator()