import time
from core.contract import handle, reset


STREAM = [
    ("random noise", False),
    ("jarvis", True),
    ("what time is it", True),
    ("tell me a joke", True),
    ("bye", True),
]


def run_wake_tests():

    print("\n[CI] WAKE STREAM TESTS")

    reset()

    passed = 0
    failed = 0

    for msg, should_respond in STREAM:

        response = handle(msg)

        # =====================================================
        # CORRECT ASSERTION LOGIC
        # =====================================================
        if should_respond:

            if response:
                passed += 1
            else:
                failed += 1

        else:
            # noise should NOT respond
            if response == "":
                passed += 1
            else:
                failed += 1

        print(f"[WAKE TEST] input={msg} response={response}")

        time.sleep(0.01)

    print(f"Wake Stream: {passed} passed / {failed} failed")

    return {"passed": passed, "failed": failed}