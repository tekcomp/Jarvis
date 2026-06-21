import time
from core.audio_state import audio_state

ECHO_GUARD_SECONDS = 1.2


def should_block_audio():

    now = time.time()

    if audio_state.tts_active:
        return True

    if now - audio_state.last_tts_end < ECHO_GUARD_SECONDS:
        return True

    return False