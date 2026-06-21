import time
import threading
from core.interruption import is_interrupted


class AudioState:
    """
    Jarvis Audio State Machine v3.1

    Handles:
    - VAD gating
    - TTS suppression
    - interruption-aware mic control
    - crash-safe recovery from TTS failure
    """

    def __init__(self):
        self._lock = threading.Lock()

        self.is_speaking = False

        self.mute_until = 0
        self.cooldown_until = 0

        # 🔥 NEW: interrupt safety latch
        self._last_interrupt_time = 0

    # -------------------------
    # TIME
    # -------------------------
    def _now(self):
        return time.time()

    # -------------------------
    # SPEAKING START
    # -------------------------
    def start_speaking(self, hold_seconds=1.2):
        with self._lock:
            now = self._now()

            self.is_speaking = True
            self.mute_until = now + hold_seconds

            # if interrupted recently, extend mute slightly
            if is_interrupted():
                self.mute_until += 0.3

    # -------------------------
    # SPEAKING STOP
    # -------------------------
    def stop_speaking(self, cooldown=0.6):
        with self._lock:
            now = self._now()

            self.is_speaking = False
            self.cooldown_until = now + cooldown

            # 🔥 NEW: ensure interrupt resets timing
            if is_interrupted():
                self.cooldown_until += 0.2

    # -------------------------
    # INTERRUPT HOOK (CALLED FROM VAD)
    # -------------------------
    def on_interrupt(self):
        with self._lock:
            self._last_interrupt_time = self._now()

            # force immediate mic re-enable after short debounce
            self.mute_until = self._now() + 0.15
            self.cooldown_until = self._now() + 0.15
            self.is_speaking = False

    # -------------------------
    # MIC GATE
    # -------------------------
    def mic_allowed(self) -> bool:
        now = self._now()

        # 1. hard block while speaking
        if self.is_speaking:
            return False

        # 2. interrupt override (brief safety window only)
        if is_interrupted():
            if now - self._last_interrupt_time < 0.25:
                return False

        # 3. TTS buffer window
        if now < self.mute_until:
            return False

        # 4. post-TTS cooldown
        if now < self.cooldown_until:
            return False

        return True

    # -------------------------
    # RESET (IMPORTANT FOR CI + TESTS)
    # -------------------------
    def reset(self):
        with self._lock:
            self.is_speaking = False
            self.mute_until = 0
            self.cooldown_until = 0
            self._last_interrupt_time = 0

    # -------------------------
    # DEBUG
    # -------------------------
    def debug(self):
        return {
            "is_speaking": self.is_speaking,
            "mute_left": max(0, self.mute_until - self._now()),
            "cooldown_left": max(0, self.cooldown_until - self._now()),
            "interrupt_active": is_interrupted(),
            "mic_allowed": self.mic_allowed()
        }


audio_state = AudioState()