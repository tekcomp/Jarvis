# ==============================
# core/import_guard.py (ARCHITECTURE LOCK v1)
# ==============================

import sys


BANNED_IMPORTS = {
    "core.brain.handle",
    "core.brain.stream_response",
    "core.brain.reset",
}


def enforce_import_rules():
    """
    Prevents forbidden imports at runtime.
    """

    for mod in list(sys.modules.keys()):
        if mod in BANNED_IMPORTS:
            raise ImportError(
                f"[ARCHITECTURE LOCK] Forbidden import detected: {mod}. "
                f"Use core.contract instead."
            )