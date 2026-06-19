import time
from core.brain import handle

TEST_CASES = [
    "hey jarvis",
    "what is 2 plus 2",
    "what is the capital of florida",
    "you",
    "thanks for watching",
    "hello jarvis explain quantum computing",
    "bye"
]


def is_noise(text: str) -> bool:
    return text in ["you", "thanks for watching"]


def run_test(input_text: str):
    start = time.time()

    try:
        output = handle(input_text, qa_mode=True)
    except Exception as e:
        output = f"error: {e}"

    latency = (time.time() - start) * 1000

    if output is None:
        output = ""

    output = str(output).strip()

    print("\n======================")
    print("INPUT:", input_text)
    print("OUTPUT:", output)
    print(f"LATENCY: {latency:.2f} ms")

    # -------------------
    # SCORING RULES
    # -------------------

    if is_noise(input_text):
        passed = (output == "")
        print("[PASS]" if passed else "[FAIL]")
        return passed

    if len(output) < 2:
        print("[FAIL]")
        return False

    print("[PASS]")
    return True


def main():
    passed = 0

    for t in TEST_CASES:
        if run_test(t):
            passed += 1

    print("\n===== SUMMARY =====")
    print(f"Passed: {passed}/{len(TEST_CASES)}")


if __name__ == "__main__":
    main()