"""Test the transcript logger in core.alive_kernel.

Verifies that:
  - _log_transcript writes one line per event
  - Each line has an ISO-8601 timestamp + ROLE: text
  - The file is created if missing
  - Empty / None text is silently dropped
  - Failures inside the logger don't propagate

Run: python tests/test_transcript.py
"""
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

# Force a fresh transcript.log so the test is hermetic.
LOG_PATH = os.path.join(ROOT, "logs", "transcript.log")
if os.path.exists(LOG_PATH):
    os.remove(LOG_PATH)

# Importing alive_kernel has side effects (it instantiates singletons and
# starts the heartbeat / TTS worker). We only need the logger helper,
# so we import the module to make sure _log_transcript is bound, but
# we don't run the kernel.
import core.alive_kernel as ak  # noqa: E402


def _read_log():
    if not os.path.exists(LOG_PATH):
        return []
    with open(LOG_PATH, "r", encoding="utf-8") as f:
        return [l.rstrip("\n") for l in f if l.strip()]


def _check(name: str, got, expected) -> bool:
    ok = got == expected
    mark = "PASS" if ok else "FAIL"
    print(f"  [{mark}] {name}: got={got!r}  expected={expected!r}")
    return ok


def _extract_role_and_tag(line: str):
    """Parse "<ts> [tag] ROLE: text" or "<ts> ROLE: text" into (role, tag, text)."""
    parts = line.split(" ", 1)
    if len(parts) != 2:
        return None, None, None
    ts, body = parts
    tag = ""
    if body.startswith("["):
        end = body.find("]")
        if end > 0:
            tag = body[1:end]
            body = body[end + 1:].lstrip()
    role_end = body.find(":")
    if role_end < 0:
        return None, None, None
    role = body[:role_end]
    text = body[role_end + 1:].lstrip()
    return role, tag, text


def test_writes_one_line_per_event():
    print("test_writes_one_line_per_event:")
    if os.path.exists(LOG_PATH):
        os.remove(LOG_PATH)
    ak._log_transcript("USER", "jarvis what time is it")
    ak._log_transcript("JARVIS", "The current time is 01:30:00.")
    lines = _read_log()
    ok = _check("line count", len(lines), 2)
    if ok:
        r0, _t0, _x0 = _extract_role_and_tag(lines[0])
        r1, _t1, _x1 = _extract_role_and_tag(lines[1])
        ok &= _check("line 0 role", r0, "USER")
        ok &= _check("line 1 role", r1, "JARVIS")
        ok &= _check("line 0 text", "jarvis what time is it" in lines[0], True)
        ok &= _check("line 1 text", "The current time is 01:30:00." in lines[1], True)
    return ok


def test_intent_tag_optional():
    print("test_intent_tag_optional:")
    if os.path.exists(LOG_PATH):
        os.remove(LOG_PATH)
    # No intent tag -> line should not have square brackets.
    ak._log_transcript("USER", "no tag")
    # With intent tag -> line should have "[joke] " between ts and role.
    ak._log_transcript("JARVIS", "with tag", intent="joke")
    lines = _read_log()
    ok = _check("line count", len(lines), 2)
    if ok:
        r0, t0, _ = _extract_role_and_tag(lines[0])
        r1, t1, _ = _extract_role_and_tag(lines[1])
        ok &= _check("untagged role", r0, "USER")
        ok &= _check("untagged tag is empty", t0, "")
        ok &= _check("untagged has no brackets", "[" in lines[0], False)
        ok &= _check("tagged role", r1, "JARVIS")
        ok &= _check("tagged tag", t1, "joke")
        ok &= _check("tagged has brackets", "[joke]" in lines[1], True)
    return ok


def test_classify_canned_intent():
    print("test_classify_canned_intent:")
    cases = [
        ("playful mode", "mode"),
        ("jarvis mode", "mode"),
        ("assistant mode", "mode"),
        ("tell me a joke", "joke"),
        ("what time is it", "time"),
        ("what is the date", "date"),
        ("goodbye", "shutdown"),
        ("holidays in june", "holiday"),
        ("what about mexico", "canned"),
    ]
    ok = True
    for text, want in cases:
        got = ak._classify_canned_intent(text)
        mark = "PASS" if got == want else "FAIL"
        print(f"  [{mark}] {text!r:30s} -> {got!r}  (want {want!r})")
        ok &= got == want
    return ok


def test_iso_timestamp_format():
    print("test_iso_timestamp_format:")
    if os.path.exists(LOG_PATH):
        os.remove(LOG_PATH)
    ak._log_transcript("USER", "test")
    lines = _read_log()
    if not lines:
        print("  [FAIL] no lines written")
        return False
    # Expected: "2026-07-01T01:33:43 USER: test"
    parts = lines[0].split(" ", 1)
    if len(parts) != 2:
        print(f"  [FAIL] bad line shape: {lines[0]!r}")
        return False
    ts, body = parts
    ok = (
        len(ts) == 19  # YYYY-MM-DDTHH:MM:SS
        and ts[4] == "-"
        and ts[7] == "-"
        and ts[10] == "T"
        and ts[13] == ":"
        and ts[16] == ":"
    )
    print(f"  [{'PASS' if ok else 'FAIL'}] timestamp {ts!r} matches ISO-8601")
    return ok


def test_empty_text_silently_dropped():
    print("test_empty_text_silently_dropped:")
    if os.path.exists(LOG_PATH):
        os.remove(LOG_PATH)
    ak._log_transcript("USER", "")
    ak._log_transcript("JARVIS", None)
    lines = _read_log()
    return _check("line count after empty writes", len(lines), 0)


def test_thread_safe():
    print("test_thread_safe:")
    if os.path.exists(LOG_PATH):
        os.remove(LOG_PATH)
    import threading

    def writer(role, prefix):
        for i in range(20):
            ak._log_transcript(role, f"{prefix}-{i}")

    threads = [
        threading.Thread(target=writer, args=("USER", "u")),
        threading.Thread(target=writer, args=("JARVIS", "j")),
        threading.Thread(target=writer, args=("USER", "k")),
    ]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    lines = _read_log()
    ok = _check("line count after 3 threads x 20 writes", len(lines), 60)
    # Every line should parse as a valid event.
    for ln in lines:
        parts = ln.split(" ", 1)
        if len(parts) != 2:
            print(f"  [FAIL] malformed line: {ln!r}")
            ok = False
            break
    return ok


def test_failure_does_not_raise():
    print("test_failure_does_not_raise:")
    # Pass something that should fail gracefully inside the logger.
    # Object with a non-coercible __str__ would normally raise.
    class Bad:
        def __str__(self):
            raise RuntimeError("boom")

    try:
        ak._log_transcript("USER", Bad())  # type: ignore[arg-type]
    except Exception as e:
        print(f"  [FAIL] _log_transcript raised: {e}")
        return False
    print("  [PASS] _log_transcript did not raise")
    return True


def test_log_rating_writes_line():
    print("test_log_rating_writes_line:")
    if os.path.exists(LOG_PATH):
        os.remove(LOG_PATH)
    ak._log_rating(1, "test")
    ak._log_rating(-1)
    ak._log_rating(0, "neutral")
    lines = _read_log()
    ok = _check("line count", len(lines), 3)
    if ok:
        # Line 0: rating 1
        ok &= _check("up rating format", "RATING: +1 test" in lines[0], True)
        # Line 1: rating -1, no comment
        ok &= _check("down rating format", "RATING: -1" in lines[1], True)
        # Line 2: rating 0
        ok &= _check("zero rating format", "RATING: +0" in lines[2] or "RATING: 0" in lines[2], True)
    return ok


def test_log_rating_rejects_invalid():
    print("test_log_rating_rejects_invalid:")
    if os.path.exists(LOG_PATH):
        os.remove(LOG_PATH)
    ak._log_rating(2, "should be dropped")
    ak._log_rating(-5)
    lines = _read_log()
    return _check("line count after invalid writes", len(lines), 0)


def test_remember_and_get_last_jarvis_ts():
    print("test_remember_and_get_last_jarvis_ts:")
    # No JARVIS line yet
    before = ak.get_last_jarvis_ts()
    ak._remember_jarvis_ts("2026-07-01T01:30:00")
    after = ak.get_last_jarvis_ts()
    ak._remember_jarvis_ts("2026-07-01T01:31:00")
    final = ak.get_last_jarvis_ts()
    return _check("latest ts remembered", (before, after, final),
                  (None, "2026-07-01T01:30:00", "2026-07-01T01:31:00"))


def test_rate_last_response_routes_to_log():
    print("test_rate_last_response_routes_to_log:")
    if os.path.exists(LOG_PATH):
        os.remove(LOG_PATH)
    # Reset module-level JARVIS ts so we can test the "no JARVIS yet" path.
    ak._remember_jarvis_ts("")  # empty string is falsy; get_last_jarvis_ts returns it
    # Force-clear: monkey-patch the global
    saved = ak._LAST_JARVIS_TS
    ak._LAST_JARVIS_TS = None
    try:
        # No JARVIS line yet -> error
        msg = ak.rate_last_response(1)
        ok = _check("no-jarvis message", "no JARVIS response" in msg, True)
        # After remembering a JARVIS ts, rating should succeed
        ak._remember_jarvis_ts("2026-07-01T01:30:00")
        msg = ak.rate_last_response(1, "great")
        ok &= _check("thumbs up message", "thumbs up" in msg, True)
        lines = _read_log()
        ok &= _check("rating line written", len(lines), 1)
        ok &= _check("rating content", "RATING: +1 great" in lines[0], True)
    finally:
        ak._LAST_JARVIS_TS = saved
    return ok


def run_transcript_tests() -> dict:
    print("\n[CI] TRANSCRIPT LOGGER TESTS")
    results = [
        test_writes_one_line_per_event(),
        test_intent_tag_optional(),
        test_classify_canned_intent(),
        test_iso_timestamp_format(),
        test_empty_text_silently_dropped(),
        test_thread_safe(),
        test_failure_does_not_raise(),
        test_log_rating_writes_line(),
        test_log_rating_rejects_invalid(),
        test_remember_and_get_last_jarvis_ts(),
        test_rate_last_response_routes_to_log(),
    ]
    # Cleanup the test artifact so it doesn't pollute the live log.
    if os.path.exists(LOG_PATH):
        os.remove(LOG_PATH)
    passed = sum(1 for r in results if r)
    failed = sum(1 for r in results if not r)
    print(f"transcript: {passed} passed / {failed} failed")
    return {"passed": passed, "failed": failed}


if __name__ == "__main__":
    res = run_transcript_tests()
    sys.exit(0 if res["failed"] == 0 else 1)
