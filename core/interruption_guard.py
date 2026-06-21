import time
from core.audio_state import audio_state

# REAL interrupt function (original reference saved here)
_original_interrupt = None

# STATE MACHINE
_last_session_id = 0
_interrupt_fired = False
_last_fire_time = 0

COOLDOWN = 1.0


def install_interrupt_guard(interrupt_fn):
    """
    Replace system interrupt with guarded version
    """
    global _original_interrupt
    _original_interrupt = interrupt_fn


def guarded_interrupt():
    """
    CI-safe interrupt:
    - max 1 per session
    - cooldown enforced
    """
    global _interrupt_fired, _last_fire_time

    now = time.time()

    # BLOCK spam
    if _interrupt_fired:
        return

    if (now - _last_fire_time) < COOLDOWN:
        return

    _interrupt_fired = True
    _last_fire_time = now

    print("[INTERRUPT] FIRED")

    if _original_interrupt:
        _original_interrupt()

    try:
        audio_state.on_interrupt()
    except:
        pass


def reset_interrupt_session():
    """
    Called every TTS start
    """
    global _interrupt_fired
    _interrupt_fired = False