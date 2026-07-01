# tests/test_brain.py
#
# Tests the real core.brain pipeline that the running Jarvis kernel uses.
# Previously this module imported core.spec.spec_loader, a parallel contract
# layer that returned canned responses for "what time is it", "tell me a
# joke", bare "jarvis", etc. The real brain behaves differently:
#
#   - bare "jarvis" never reaches route_intent (wake_gate strips it first)
#   - "jarvis what time is it" -> wake_gate strips to "what time is it",
#     THEN route_intent is called
#   - "tell me a joke" -> route_intent handles via word-boundary regex
#   - "random nonsense" -> returns None, falls through to LLM
#
# So we test route_intent against the text the kernel actually passes in
# (post-wake-strip) and assert the real classification.
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from core import brain
from core.wake_gate import strip_wake_word
from core.personality_engine_v2 import get_engine


# (user_text, expected_classification)
# `user_text` is the *raw* speech, mirroring what the kernel's STT layer
# would produce. The test strips the wake word before calling route_intent,
# exactly as the live kernel does.
TESTS = [
    ("what time is it", "time"),
    ("what is the date", "date"),
    ("tell me a joke", "joke"),
    ("jarvis what time is it", "time"),   # wake stripped -> "what time is it"
    ("jarvis tell me a joke", "joke"),
    ("random nonsense", "none"),          # no canned match -> None
    ("playful mode", "mode"),
    ("jarvis mode", "mode"),
    ("jarvis version", "version"),
    ("jarvis status", "version"),
    ("jarvis memory", "memory"),
    ("jarvis what do you remember", "memory"),
]


def classify(output) -> str:
    """Map a brain response string to a classification label.

    Note: joke responses are randomly picked from a 70-entry bank across
    six styles, so we can't fingerprint them. We assert "joke" iff the
    response is a non-empty string whose first sentence ends with a
    typical joke terminator ('.', '!', '?'). Mode responses all contain
    either "switched to" or "activated" or the bare-mode hint phrase.
    """
    if output is None:
        return "none"
    o = str(output).strip().lower()
    if not o:
        return "none"
    if "time is" in o:
        return "time"
    if "today is" in o:
        return "date"
    # Version / self-report: contains "model" + "kernel pid" signature.
    if "model" in o and "kernel pid" in o:
        return "version"
    # Memory / self-report: contains "in memory" or "don't have anything".
    if "in memory" in o or "don't have anything" in o or "do not have anything" in o:
        return "memory"
    # Mode: explicit "switched to X mode" / "X mode activated" / bare hint.
    if "switched to" in o or "activated" in o or "current mode is" in o:
        return "mode"
    # Joke: any non-empty response that doesn't match the above.
    # (The real bank covers many generations; we trust that route_intent
    # either returns a joke string or None.)
    if o.endswith((".", "!", "?")):
        return "joke"
    return "unknown"


def _run_one(text: str, expected: str) -> tuple[bool, str]:
    """Apply the same preprocessing the live kernel does, then classify."""
    # Reset state per test so mode/memory don't bleed across.
    engine = get_engine()
    engine.mode = "jarvis"
    brain.reset_memory()

    # Mimic alive_kernel: strip wake word if present, then call route_intent.
    stripped = strip_wake_word(text)
    out = brain.route_intent(stripped) if stripped else None
    result = classify(out)
    return result == expected, result


def run_brain_tests():
    print("\n[CI] BRAIN TESTS (real core.brain pipeline)")

    passed = 0
    failed = 0

    for text, expected in TESTS:
        ok, result = _run_one(text, expected)
        mark = "PASS" if ok else "FAIL"
        print(f"  [{mark}] INPUT={text!r:30s}  result={result:8s}  expected={expected}")
        if ok:
            passed += 1
        else:
            failed += 1

    print(f"Brain: {passed} passed / {failed} failed")
    return {"passed": passed, "failed": failed}