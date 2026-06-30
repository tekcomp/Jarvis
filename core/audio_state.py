# =========================================================
# core/audio_state.py
# =========================================================

import time
from dataclasses import dataclass

# Single source of truth for "is TTS speaking / just spoke" — referenced by
# both audio_state (mic gate) and stt.whisper (echo suppression via DuplexGuard).
try:
    from core.duplex_guard import duplex as _duplex
except Exception:  # keep module importable for tooling/parsing
    _duplex = None


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
    def tts_started(self, hold_seconds: float = 0.0):

        self.tts_active = True
        self.last_tts_start = time.time()
        # Default mute window; longer if caller requested.
        hold = hold_seconds if (hold_seconds and hold_seconds > 0) else 2.5
        if hold > self.echo_guard_seconds:
            self.echo_guard_seconds = hold
        if _duplex is not None:
            try:
                _duplex.start(hold_seconds=hold)
            except Exception:
                pass

    def tts_finished(self):

        self.tts_active = False
        self.last_tts_end = time.time()
        if _duplex is not None:
            try:
                _duplex.stop()
            except Exception:
                pass

    # Legacy / cross-process aliases used by tts/voice_async._tts_worker.
    # Do NOT remove without updating the async TTS worker first.
    def start_speaking(self, hold_seconds: float = 0.0):
        self.tts_started()
        # Default mute window if caller didn't specify. Edge-tts round-trip
        # + playback routinely exceeds 1.5s in reflected rooms.
        hold = hold_seconds if (hold_seconds and hold_seconds > 0) else 2.5
        if hold > self.echo_guard_seconds:
            self.echo_guard_seconds = hold
        # Mirror the mute window into the global DuplexGuard so stt.whisper
        # also rejects echo transcriptions during this window.
        if _duplex is not None:
            try:
                _duplex.start(hold_seconds=hold)
            except Exception:
                pass

    def stop_speaking(self):
        self.tts_finished()
        if _duplex is not None:
            try:
                _duplex.stop()
            except Exception:
                pass

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