import threading

# =========================================================
# GLOBAL SHUTDOWN STATE
# =========================================================

_shutdown_event = threading.Event()


def is_shutdown() -> bool:
    """
    Returns True once shutdown has been triggered.
    """
    return _shutdown_event.is_set()


def trigger_shutdown(reason="unknown") -> bool:
    """
    Triggers shutdown exactly once.

    Returns:
        True  -> first shutdown request
        False -> shutdown already active
    """

    if _shutdown_event.is_set():
        return False

    _shutdown_event.set()

    print(f"\n[SYSTEM] SAFE SHUTDOWN TRIGGERED ({reason})")

    return True


def reset_shutdown():
    """
    Used only for tests / CI.
    """
    _shutdown_event.clear()