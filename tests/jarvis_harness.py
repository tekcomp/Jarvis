import sys
import os

# -------------------------------------------------
# FIX IMPORT PATH (CI SAFE)
# -------------------------------------------------
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from core.brain import handle


# -------------------------------------------------
# TEST CASES (behavior contracts)
# -------------------------------------------------
TESTS = [
    ("what time is it", "time"),
    ("what is the date", "date"),
    ("tell me a joke", "joke"),
    ("jarvis", "wake"),
    ("jarvis what time is it", "time"),
    ("random nonsense", "none"),
]


# -------------------------------------------------
# TEST RUNNER
# -------------------------------------------------
def run_tests():
    print("\n==============================")
    print("[JARVIS TEST HARNESS v1]")
    print("==============================\n")

    passed = 0
    failed = 0

    for input_text, expected in TESTS:

        # reset brain state per test (IMPORTANT)
        reset_brain_state()

        output = handle(input_text.lower().strip())
        result_type = classify(output)

        ok = result_type == expected

        print(f"INPUT   : {input_text}")
        print(f"OUTPUT  : {output}")
        print(f"EXPECT  : {expected}")
        print(f"GOT     : {result_type}")

        if ok:
            print("RESULT  : PASS\n")
            passed += 1
        else:
            print("RESULT  : FAIL\n")
            failed += 1

    print("==============================")
    print(f"TOTAL PASS: {passed}")
    print(f"TOTAL FAIL: {failed}")
    print("==============================\n")

    # CI EXIT CODE
    sys.exit(0 if failed == 0 else 1)


# -------------------------------------------------
# RESET STATE (IMPORTANT FOR WAKE WORD SYSTEMS)
# -------------------------------------------------
def reset_brain_state():
    """
    Ensures each test runs independently.
    Prevents wake-word memory leaks.
    """
    try:
        import core.brain as brain
        brain.active = False
    except Exception:
        pass


# -------------------------------------------------
# CLASSIFIER (HARDENED)
# -------------------------------------------------
def classify(output: str) -> str:

    if not output:
        return "none"

    o = output.lower()

    if "time is" in o:
        return "time"

    if "today is" in o or "date" in o:
        return "date"

    if "reward function" in o:
        return "joke"

    if "yes?" in o:
        return "wake"

    if "didn't understand" in o:
        return "none"

    return "unknown"


if __name__ == "__main__":
    run_tests()