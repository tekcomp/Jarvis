import time
import threading


class DuplexGuard:
    """
    Full duplex control system:
    - Prevents VAD capturing TTS audio
    - Time-based ignore window (stable vs flags)
    """

    def __init__(self):
        self._lock = threading.Lock()
        self._speaking = False
        self._mute_until = 0

    def start(self, hold_seconds=1.5):
        with self._lock:
            self._speaking = True
            self._mute_until = time.time() + hold_seconds

    def stop(self):
        with self._lock:
            self._speaking = False

    def muted(self):
        return time.time() < self._mute_until or self._speaking


# singleton
duplex = DuplexGuard()