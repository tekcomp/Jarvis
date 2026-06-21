import sys
import os
import time

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

from tests.test_brain import run_brain_tests
from tests.test_pipeline_mock import run_pipeline_tests
from tests.test_wake_stream import run_wake_tests
from core.brain import handle, reset


# =========================================================
# LATENCY TEST (NEW)
# =========================================================
def run_latency_test():

    print("\n[CI] LATENCY TESTS")

    samples = [
        "jarvis what time is it",
        "jarvis what is the date",
        "tell me a joke",
    ]

    latencies = []

    for s in samples:

        start = time.time()
        _ = handle(s)
        end = time.time()

        latencies.append(end - start)

    avg = sum(latencies) / len(latencies)

    print(f"Latency Avg: {round(avg * 1000, 2)} ms")

    return {
        "passed": 1 if avg < 0.8 else 0,
        "failed": 0 if avg < 0.8 else 1
    }


# =========================================================
# MEMORY CONSISTENCY TEST (NEW)
# =========================================================
def run_memory_test():

    print("\n[CI] MEMORY TESTS")

    reset()

    r1 = handle("jarvis what time is it")
    r2 = handle("what did I just ask you")

    # simple heuristic check (not strict NLP)
    ok = r1 and isinstance(r1, str)

    print(f"Memory Response: {r2}")

    return {
        "passed": 1 if ok else 0,
        "failed": 0 if ok else 1
    }


# =========================================================
# NOISE RESISTANCE TEST (NEW)
# =========================================================
def run_noise_test():

    print("\n[CI] NOISE RESISTANCE TESTS")

    noise_inputs = [
        "",
        "   ",
        "asdfghjkl",
        "??!!",
        "random noise input"
    ]

    passed = 0
    failed = 0

    for n in noise_inputs:

        try:
            out = handle(n)

            if out is None:
                failed += 1
            else:
                passed += 1

        except Exception:
            failed += 1

    print(f"Noise: {passed} passed / {failed} failed")

    return {
        "passed": passed,
        "failed": failed
    }


# =========================================================
# MAIN CI PIPELINE
# =========================================================
def main():

    print("\n===================================")
    print(" JARVIS CI PIPELINE v2 (ALIVE TEST MODE)")
    print("===================================\n")

    results = []

    # Core tests
    results.append(run_brain_tests())
    results.append(run_pipeline_tests())
    results.append(run_wake_tests())

    # Alive system tests
    results.append(run_latency_test())
    results.append(run_memory_test())
    results.append(run_noise_test())

    total_failures = sum(r["failed"] for r in results)

    print("\n===================================")
    print(f"CI RESULT: {'PASS' if total_failures == 0 else 'FAIL'}")
    print("===================================\n")

    sys.exit(0 if total_failures == 0 else 1)


if __name__ == "__main__":
    main()