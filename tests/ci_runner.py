import sys
import os

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

from tests.test_brain import run_brain_tests
from tests.test_pipeline_mock import run_pipeline_tests
from tests.test_wake_stream import run_wake_tests

# -------------------------------------------------
# CRITICAL: IMPORT BRAIN RESET HOOK
# -------------------------------------------------
from core.brain import reset


# =================================================
# CI SAFE WRAPPER
# ensures no state leaks between test suites
# =================================================
def run_with_reset(test_fn, name: str):
    print(f"\n[CI] {name}")

    try:
        reset()  # HARD RESET before suite
        result = test_fn()
        reset()  # HARD RESET after suite

        return result

    except Exception as e:
        print(f"[CI ERROR] {name}: {e}")

        return {
            "passed": 0,
            "failed": 999
        }


def main():

    print("\n===================================")
    print(" JARVIS CI PIPELINE v1 (HARDENED)")
    print("===================================\n")

    results = []

    # -------------------------------------------------
    # BRAIN TESTS
    # -------------------------------------------------
    results.append(run_with_reset(run_brain_tests, "BRAIN TESTS"))

    # -------------------------------------------------
    # PIPELINE MOCK TESTS
    # -------------------------------------------------
    results.append(run_with_reset(run_pipeline_tests, "PIPELINE MOCK TESTS"))

    # -------------------------------------------------
    # WAKE STREAM TESTS (MOST STATE-SENSITIVE)
    # -------------------------------------------------
    results.append(run_with_reset(run_wake_tests, "WAKE STREAM TESTS"))

    # -------------------------------------------------
    # FINAL SUMMARY
    # -------------------------------------------------
    total_failures = sum(r["failed"] for r in results)

    print("\n===================================")
    print(f"CI RESULT: {'PASS' if total_failures == 0 else 'FAIL'}")
    print("===================================\n")

    sys.exit(0 if total_failures == 0 else 1)


if __name__ == "__main__":
    main()