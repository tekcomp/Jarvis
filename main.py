# ==============================
# main.py (CI-GATED BOOTSTRAP)
# ==============================

import sys

from tests.ci_runner import run_ci_tests
from core.alive_kernel import start_kernel
import builtins
import time as _time

# protect critical names
assert callable(_time.strftime)
import builtins


assert callable(_time.strftime), "time module overwritten!"

def debug_types():
    import core.brain as brain

    print("route_intent:", type(brain.route_intent))
    print("stream_response:", type(brain.stream_response))

debug_types()

def boot():

    print("[SYSTEM] BOOT SEQUENCE INIT")

    # ------------------------------
    # CI GATE (PRE-FLIGHT CHECK)
    # ------------------------------
    print("[CI] Running pre-flight tests...")

    try:
        ok = run_ci_tests()

    except Exception as e:
        print(f"[CI] CRASH DURING TESTS: {e}")
        sys.exit(1)

    if not ok:
        print("[CI] FAILED - SYSTEM BLOCKED")
        sys.exit(1)

    print("[CI] ALL TESTS PASSED")
    print("[SYSTEM] STARTING KERNEL")

    # ------------------------------
    # START SYSTEM
    # ------------------------------
    start_kernel()


if __name__ == "__main__":
    boot()