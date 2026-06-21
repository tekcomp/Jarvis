# ==============================
# core/runtime_state.py (AGENT v2 STATE CORE)
# ==============================
import time
import threading

# -------------------------------------------------
# GLOBAL SYSTEM STATE FLAGS (THREAD SAFE)
# -------------------------------------------------

system_busy = threading.Event()
tts_active = threading.Event()
shutdown_flag = threading.Event()

audio_mute_until = 0.0
last_tts_hash = None

# -------------------------------------------------
# STATE HELPERS
# -------------------------------------------------

def set_busy(value: bool):
    if value:
        system_busy.set()
    else:
        system_busy.clear()


def is_busy() -> bool:
    return system_busy.is_set()


def set_tts(value: bool):
    if value:
        tts_active.set()
    else:
        tts_active.clear()


def is_tts_active() -> bool:
    return tts_active.is_set()


def is_shutdown() -> bool:
    return shutdown_flag.is_set()


def trigger_shutdown(reason: str = "unknown"):
    print(f"[SYSTEM] SHUTDOWN TRIGGERED ({reason})")
    shutdown_flag.set()