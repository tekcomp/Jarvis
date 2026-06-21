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

        self._speech_frames = 0
        self.MIN_SPEECH_FRAMES = 2

        self._last_frame = -1
        self._prev_speech = False

    # -----------------------------
    # TRACE
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

        self._speech_frames = 0
        self._last_frame = -1
        self._prev_speech = False

        self.session_id += 1
        self.trace("SYS", "TTS_START", f"session={self.session_id}")

    def stop_tts(self):
        self.tts_state = TTS_IDLE
        self.interrupt_state = INTERRUPT_CLOSED
        self.trace("SYS", "TTS_STOP")

    # -----------------------------
    # CI EVALUATION
    # -----------------------------
    def evaluate(self, frame_id, user_speaking, tts_streaming=True):

        if self.fired:
            return False

        if not tts_streaming:
            return False

        if frame_id == self._last_frame:
            return False

        self._last_frame = frame_id

        if self.tts_state != TTS_SPEAKING:
            return False

        if self.interrupt_state != INTERRUPT_OPEN:
            return False

        # debounce speech
        if user_speaking:
            self._speech_frames += 1
        else:
            self._speech_frames = 0
            self._prev_speech = False
            return False

        if self._speech_frames < self.MIN_SPEECH_FRAMES:
            return False

        # edge detect
        if not self._prev_speech and user_speaking:

            self.fired = True
            self.interrupt_state = INTERRUPT_CLOSED

            self.trace(frame_id, "INTERRUPT_FIRED", "<<< CI FINAL >>>")

            self._prev_speech = True
            return True

        self._prev_speech = True
        return False