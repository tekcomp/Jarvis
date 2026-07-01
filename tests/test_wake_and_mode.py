"""Tests for the wake-strip edge case and the bare-mode intent branch.

Run: python tests/test_wake_and_mode.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.wake_gate import strip_wake_word, contains_wake_word
from core import brain
from core.personality_engine_v2 import get_engine


def _check(name, got, expected):
    ok = got == expected
    mark = "PASS" if ok else "FAIL"
    print(f"  [{mark}] {name}: got={got!r}  expected={expected!r}")
    return ok


def test_wake_strip():
    print("test_wake_strip:")
    cases = [
        ("jarvis what time is it", "what time is it"),
        ("hey jarvis tell me a joke", "tell me a joke"),
        ("okay jarvis write a haiku", "write a haiku"),
        ("ok jarvis hello", "hello"),
        # Edge case: stripping leaves "mode" (only 4 chars but > 2, so no salvage).
        # route_intent handles "mode" with a helpful "Current mode is X" reply.
        ("jarvis jarvis mode", "mode"),
        ("jarvis", ""),                            # wake-only -> empty
        ("jarvis playful mode", "playful mode"),
        ("", ""),
    ]
    ok = True
    for txt, want in cases:
        ok &= _check(f"strip({txt!r})", strip_wake_word(txt), want)
    return ok


def test_contains_wake():
    print("\ntest_contains_wake:")
    cases = [
        ("jarvis hello", True),
        ("hey jarvis", True),
        ("thanks for watching", False),
        ("", False),
        ("JARVIS", True),  # case-insensitive
    ]
    ok = True
    for txt, want in cases:
        ok &= _check(f"contains({txt!r})", contains_wake_word(txt), want)
    return ok


def test_bare_mode_intent():
    print("\ntest_bare_mode_intent (no LLM call — these are canned):")
    engine = get_engine()
    engine.mode = "jarvis"
    expected_substr = "Current mode is jarvis"
    cases = [
        "mode",
        "modes",
        "switch mode",
        "switch modes",
    ]
    ok = True
    for txt in cases:
        got = brain.route_intent(txt) or ""
        ok &= _check(
            f"route_intent({txt!r}) contains {expected_substr!r}",
            expected_substr in got,
            True,
        )
    return ok


def test_word_boundary_holds():
    print("\ntest_word_boundary_holds (regression):")
    cases = [
        # (input, must_NOT_contain_substring)
        ("12 times 13", "current time"),
        ("the clockwork has been wound tight", "current time"),
    ]
    ok = True
    for txt, must_not in cases:
        got = brain.route_intent(txt)
        ok &= _check(
            f"route_intent({txt!r}) does not contain {must_not!r}",
            must_not.lower() in (got or "").lower(),
            False,
        )
    return ok


def run_wake_and_mode_tests() -> dict:
    """CI entry point: returns {"passed": N, "failed": M}."""
    results = [
        test_wake_strip(),
        test_contains_wake(),
        test_bare_mode_intent(),
        test_word_boundary_holds(),
    ]
    passed = sum(1 for r in results if r)
    failed = sum(1 for r in results if not r)
    print(f"wake_and_mode: {passed} passed / {failed} failed")
    return {"passed": passed, "failed": failed}


def main():
    results = [
        test_wake_strip(),
        test_contains_wake(),
        test_bare_mode_intent(),
        test_word_boundary_holds(),
    ]
    passed = sum(results)
    total = len(results)
    print(f"\n{passed}/{total} test groups passed")
    sys.exit(0 if passed == total else 1)


if __name__ == "__main__":
    main()
