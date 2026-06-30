# =========================================================
# core/audio_state.py
# =========================================================

import time
from dataclasses import dataclass


@dataclass
class AudioState:

    tts_active: bool = False

    last_tts_start: float = 0.0
    last_tts_end: float = 0.0

    # blocks mic briefly after TTS finishes
    echo_guard_seconds: float = 1.5

    # -----------------------------------------------------
    # TTS EVENTS (canonical: tts_started/tts_finished)
    # Aliases for legacy callers (tts/voice_async.py)
    # -----------------------------------------------------
    def tts_started(self):

        self.tts_active = True
        self.last_tts_start = time.time()

    def tts_finished(self):

        self.tts_active = False
        self.last_tts_end = time.time()

    # Legacy / cross-process aliases used by tts/voice_async._tts_worker.
    # Do NOT remove without updating the async TTS worker first.
    def start_speaking(self, hold_seconds: float = 0.0):
        self.tts_started()
        if hold_seconds and hold_seconds > self.echo_guard_seconds:
            self.echo_guard_seconds = hold_seconds

    def stop_speaking(self):
        self.tts_finished()

    # -----------------------------------------------------
    # MIC GATE
    # -----------------------------------------------------
    def mic_allowed(self) -> bool:

        # hard mute while TTS speaking
        if self.tts_active:
            return False

        # short suppression window after TTS
        if (time.time() - self.last_tts_end) < self.echo_guard_seconds:
            return False

        return True


audio_state = AudioState()