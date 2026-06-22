# =========================================================
# core/session_manager.py
# =========================================================

import time

SESSION_TIMEOUT = 30

_session_open = False
_last_activity = 0


def open_session():

    global _session_open
    global _last_activity

    _session_open = True
    _last_activity = time.time()


def touch():

    global _last_activity

    _last_activity = time.time()


def close_session():

    global _session_open

    _session_open = False


def session_active():

    global _session_open
    global _last_activity

    if not _session_open:
        return False

    if (time.time() - _last_activity) > SESSION_TIMEOUT:
        close_session()
        return False

    return True