import time
from core.brain import handle, reset


STREAM = [
    "random noise",
    "jarvis",
    "what time is it",
    "tell me a joke",
    "bye",
]


def run_wake_tests():

    print("\n[CI] WAKE STREAM TESTS")

    reset()   # 🔥 IMPORTANT FIX

    passed = 0
    failed = 0

    for msg in STREAM:

        response = handle(msg)

        if response:
            passed += 1
        else:
            failed += 1

        time.sleep(0.01)

    print(f"Wake Stream: {passed} passed / {failed} failed")

    return {"passed": passed, "failed": failed}