import sys
import os

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

from core.contract import handle, active


def run_wake_tests():

    print("\n[CI] WAKE STREAM TESTS\n")

    tests = [
        # (input, expected_active_state_after_handle)
        ("hello", False),
        ("jarvis", True),
        ("what time is it", True),
        ("random nonsense", False),
        ("jarvis tell me a joke", True),
    ]

    passed = 0
    failed = 0

    for input_text, expected in tests:

        # =====================================================
        # CRITICAL FIX: CLEAN STATE PER TEST
        # =====================================================
        try:
            from core.brain import active
            import core.brain as brain

            brain.active = False  # reset global state BEFORE test

        except Exception:
            pass

        # run pipeline
        handle(input_text)

        # re-read state after execution
        try:
            from core.brain import active
            result = active
        except Exception:
            result = False

        ok = (result == expected)

        print(f"INPUT: {input_text}")
        print(f"EXPECTED ACTIVE: {expected} | GOT: {result}")

        if ok:
            print("✅ PASS\n")
            passed += 1
        else:
            print("❌ FAIL\n")
            failed += 1

    print(f"Wake Stream: {passed} passed / {failed} failed\n")

    return {
        "passed": passed,
        "failed": failed
    }