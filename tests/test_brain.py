# tests/test_brain.py

from core.spec.spec_loader import get_spec


TESTS = [
    ("what time is it", "time"),
    ("what is the date", "date"),
    ("tell me a joke", "joke"),
    ("jarvis", "wake"),
    ("jarvis what time is it", "time"),
    ("random nonsense", "none"),
]


def classify(output: str):

    if output is None:
        return "none"

    o = str(output).lower()

    if "time is" in o:
        return "time"

    if "today is" in o:
        return "date"

    if "reward function" in o:
        return "joke"

    if "yes?" in o:
        return "wake"

    if o.strip() == "":
        return "none"

    return "unknown"


def run_brain_tests():

    print("\n[CI] BRAIN TESTS")

    spec = get_spec()

    passed = 0
    failed = 0

    for text, expected in TESTS:

        intent = spec.classify_intent(text)
        output = spec.respond(intent, text)

        result = classify(output)

        print(f"INPUT={text} EXPECTED={expected} RESULT={result} OUTPUT={output}")

        if result == expected:
            passed += 1
        else:
            failed += 1

    print(f"Brain: {passed} passed / {failed} failed")

    return {"passed": passed, "failed": failed}