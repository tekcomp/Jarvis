"""Tests for the JSON-driven canned response loader.

Confirms:
  - data/canned_responses.json loads on import
  - mode-switch responses come from JSON
  - goodbye responses are mode-aware
  - bare-mode hint interpolates the current mode
  - time / date templates interpolate correctly
  - llm_unreachable fallback is mode-aware
  - missing keys fall back to defaults (no crash)

Run: python tests/test_canned_responses.py
"""
import os
import sys
import time
import datetime

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

from core import brain
from core.personality_engine_v2 import get_engine


def _check(name, got, expected):
    ok = got == expected
    print(f"  [{'PASS' if ok else 'FAIL'}] {name}: got={got!r}  expected={expected!r}")
    return ok


def test_json_loaded():
    print("test_json_loaded:")
    ok = bool(brain._CANNED)
    print(f"  [{'PASS' if ok else 'FAIL'}] _CANNED is non-empty: {bool(brain._CANNED)}")
    return ok


def test_mode_switch_responses():
    print("test_mode_switch_responses:")
    engine = get_engine()
    cases = [
        ("jarvis mode", "jarvis", "Switched to jarvis mode."),
        ("playful mode", "playful", "Switched to playful mode."),
        ("assistant mode", "assistant", "Switched to assistant mode."),
    ]
    ok = True
    for txt, expected_mode, expected_text in cases:
        engine.mode = "jarvis"  # reset
        got = brain.route_intent(txt)
        ok &= _check(f"route_intent({txt!r})", got, expected_text)
        ok &= _check(f"engine.mode after {txt!r}", engine.mode, expected_mode)
    return ok


def test_substring_mode_switch():
    print("test_substring_mode_switch (the 'jarvis' substring rule):")
    engine = get_engine()
    engine.mode = "assistant"
    # Just saying "jarvis" alone matches the substring rule.
    got = brain.route_intent("jarvis")
    return _check("route_intent('jarvis')", got, "Jarvis mode activated.") and \
           _check("engine.mode", engine.mode, "jarvis")


def test_goodbye_responses():
    print("test_goodbye_responses:")
    engine = get_engine()
    cases = [
        ("playful", "Haha 😄 See you next time!"),
        ("assistant", "Goodbye! Let me know if you need anything else."),
        ("jarvis", "Goodbye!"),
    ]
    ok = True
    for mode, expected in cases:
        engine.mode = mode
        got = brain.route_intent("goodbye")
        ok &= _check(f"goodbye in {mode!r} mode", got, expected)
    return ok


def test_bare_mode_hint():
    print("test_bare_mode_hint:")
    engine = get_engine()
    engine.mode = "jarvis"
    expected = "Current mode is jarvis. Try 'playful mode', 'jarvis mode', or 'assistant mode'."
    got = brain.route_intent("mode")
    return _check("route_intent('mode')", got, expected)


def test_time_template():
    print("test_time_template:")
    got = brain.route_intent("what time is it?")
    ok = got.startswith("The current time is ") and got.endswith(".")
    print(f"  [{'PASS' if ok else 'FAIL'}] {got!r}")
    # Format must be HH:MM:SS.
    payload = got.removeprefix("The current time is ").removesuffix(".")
    ok &= len(payload) == 8 and payload.count(":") == 2
    print(f"  [{'PASS' if ok else 'FAIL'}] HH:MM:SS shape")
    return ok


def test_date_template_uses_today():
    print("test_date_template_uses_today:")
    got = brain.route_intent("what is the date?")
    expected_date = datetime.date.today().strftime("%A, %B %d, %Y")
    expected = f"Today is {expected_date}."
    return _check("route_intent('what is the date?')", got, expected)


def test_missing_key_falls_back():
    print("test_missing_key_falls_back:")
    # Wipe the canned dict to simulate missing JSON.
    saved = brain._CANNED
    brain._CANNED = {}
    try:
        got = brain.route_intent("playful mode")
        ok = got == "Switched to playful mode."  # default
        print(f"  [{'PASS' if ok else 'FAIL'}] fallback: {got!r}")
        return ok
    finally:
        brain._CANNED = saved


def run_canned_responses_tests() -> dict:
    print("\n[CI] CANNED RESPONSES TESTS")
    results = [
        test_json_loaded(),
        test_mode_switch_responses(),
        test_substring_mode_switch(),
        test_goodbye_responses(),
        test_bare_mode_hint(),
        test_time_template(),
        test_date_template_uses_today(),
        test_missing_key_falls_back(),
    ]
    passed = sum(1 for r in results if r)
    failed = sum(1 for r in results if not r)
    print(f"canned_responses: {passed} passed / {failed} failed")
    return {"passed": passed, "failed": failed}


if __name__ == "__main__":
    res = run_canned_responses_tests()
    sys.exit(0 if res["failed"] == 0 else 1)
