import time
import threading

TRACE = True

_trace_lock = threading.Lock()
_frame_id = 0

def next_frame():
    global _frame_id
    _frame_id += 1
    return _frame_id


def trace_interrupt(event, *, busy, speech, session, allowed, source):
    """
    CI-level deterministic interrupt trace logger
    """

    if not TRACE:
        return

    with _trace_lock:
        frame = next_frame()
        print(
            f"[CI-INT-TRACE] "
            f"frame={frame} "
            f"event={event} "
            f"busy={busy} "
            f"speech={speech} "
            f"session={session} "
            f"allowed={allowed} "
            f"source={source} "
            f"t={time.time():.3f}"
        )