import time

TTS_IDLE = 0
TTS_SPEAKING = 1

INTERRUPT_CLOSED = 0
INTERRUPT_OPEN = 1


class InterruptFSM:

    def __init__(self):
        self.tts_state = TTS_IDLE
        self.interrupt_state = INTERRUPT_CLOSED
        self.fired = False
        self.session_id = 0

        # CI CRITICAL: frame-level debounce
        self._last_frame = -1

        # CI CRITICAL: edge tracking
        self._prev_speech = False

    # -----------------------------
    # TRACE (CI REQUIRED)
    # -----------------------------
    def trace(self, frame_id, event, meta=""):
        print(
            f"[CI-FSM] frame={frame_id} "
            f"tts={self.tts_state} "
            f"int={self.interrupt_state} "
            f"fired={self.fired} "
            f"session={self.session_id} "
            f"event={event} "
            f"{meta}"
        )

    # -----------------------------
    # SESSION CONTROL
    # -----------------------------
    def start_tts(self):
        self.tts_state = TTS_SPEAKING
        self.interrupt_state = INTERRUPT_OPEN
        self.fired = False
        self._prev_speech = False
        self._last_frame = -1

        self.session_id += 1
        self.trace("SYS", "TTS_START", f"session={self.session_id}")

    def stop_tts(self):
        self.tts_state = TTS_IDLE
        self.interrupt_state = INTERRUPT_CLOSED
        self.trace("SYS", "TTS_STOP")

    # -----------------------------
    # CI STRICT EVALUATION (FINAL)
    # -----------------------------
def evaluate(self, frame_id, user_speaking, tts_streaming=True):

    # HARD GLOBAL SHORT-CIRCUIT (CI CRITICAL FIX)
    if self.fired:
        return False

    # must be inside active stream window
    if not tts_streaming:
        return False

    # avoid duplicate frame processing
    if frame_id == self._last_frame:
        return False

    self._last_frame = frame_id

    # must be valid TTS state
    if self.tts_state != TTS_SPEAKING:
        return False

    if self.interrupt_state != INTERRUPT_OPEN:
        return False

    # EDGE DETECTION ONLY
    if not self._prev_speech and user_speaking:

        self.fired = True
        self.interrupt_state = INTERRUPT_CLOSED

        # ONLY ONE TRACE (CI EXPECTS THIS)
        self.trace(frame_id, "INTERRUPT_FIRED", "<<< CI FINAL >>>")

        self._prev_speech = user_speaking
        return True

    self._prev_speech = user_speaking
    return False