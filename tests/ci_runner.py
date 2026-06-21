import sys
import os

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

from core.brain import handle, reset
from tests.test_brain import run_brain_tests
from tests.test_pipeline_mock import run_pipeline_tests
from tests.test_wake_stream import run_wake_tests


# =========================================================
# SAFE WRAPPER FOR STATEFUL SYSTEMS
# =========================================================
def run_brain_tests_isolated():
    print("\n[CI] BRAIN TESTS\n")

    reset()  # IMPORTANT: isolate state

    result = run_brain_tests()

    reset()  # cleanup after test

    print(f"Brain: {result['passed']} passed / {result['failed']} failed")
    return result


def run_pipeline_tests_isolated():
    print("\n[CI] PIPELINE MOCK TESTS\n")

    reset()

    result = run_pipeline_tests()

    reset()

    print(f"Pipeline: {result['passed']} passed / {result['failed']} failed")
    return result


def run_wake_tests_isolated():
    print("\n[CI] WAKE STREAM TESTS\n")

    reset()

    result = run_wake_tests()

    reset()

    print(f"Wake Stream: {result['passed']} passed / {result['failed']} failed")
    return result


# =========================================================
# MAIN CI RUNNER
# =========================================================
def main():

    print("\n===================================")
    print(" JARVIS CI PIPELINE v1 (ISOLATED STATE FIX)")
    print("===================================\n")

    results = []

    # -------------------------
    # ISOLATED EXECUTION LAYERS
    # -------------------------
    results.append(run_brain_tests_isolated())
    results.append(run_pipeline_tests_isolated())
    results.append(run_wake_tests_isolated())

    total_failures = sum(r["failed"] for r in results)

    print("\n===================================")
    print(f"CI RESULT: {'PASS' if total_failures == 0 else 'FAIL'}")
    print("===================================\n")

    sys.exit(0 if total_failures == 0 else 1)


if __name__ == "__main__":
    main()