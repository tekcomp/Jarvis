# core/interruption.py

_interrupt_fired = False
_last_frame_id = None

def reset():
    global _interrupt_fired, _last_frame_id

    _interrupt_fired = False
    _last_frame_id = None


def clear():
    reset()

def interrupt(frame_id=None):
    global _interrupt_fired, _last_frame_id

    if frame_id is not None and frame_id == _last_frame_id:
        print(f"[CI-INT] BLOCKED (same frame {frame_id})")
        return False

    _last_frame_id = frame_id

    if _interrupt_fired:
        print("[CI-INT] BLOCKED (already fired)")
        return False

    _interrupt_fired = True

    print("[CI-INT] ALLOWED → FIRING")

    return True


def guarded_interrupt(frame_id=None):
    return interrupt(frame_id)

def is_interrupted():
    return _interrupt_fired
