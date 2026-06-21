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
    # TTS EVENTS
    # -----------------------------------------------------
    def tts_started(self):

        self.tts_active = True
        self.last_tts_start = time.time()

    def tts_finished(self):

        self.tts_active = False
        self.last_tts_end = time.time()

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