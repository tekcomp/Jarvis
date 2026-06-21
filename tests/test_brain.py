from core.brain import handle


TESTS = [
    ("what time is it", "time"),
    ("what is the date", "date"),
    ("tell me a joke", "joke"),
    ("jarvis", "wake"),
    ("jarvis what time is it", "time"),
    ("random nonsense", "none"),
]


def classify(output: str):

    if not output:
        return "none"

    o = output.lower()

    if "time is" in o:
        return "time"

    if "today is" in o:
        return "date"

    if "reward function" in o:
        return "joke"

    if "yes?" in o:
        return "wake"

    return "unknown"


def run_brain_tests():

    print("\n[CI] BRAIN TESTS")

    passed = 0
    failed = 0

    for text, expected in TESTS:

        # reset brain state
        import core.brain as brain
        brain.active = False

        output = handle(text)
        result = classify(output)

        if result == expected:
            passed += 1
        else:
            failed += 1

    print(f"Brain: {passed} passed / {failed} failed")

    return {"passed": passed, "failed": failed}