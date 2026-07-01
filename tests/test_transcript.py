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


def test_writes_one_line_per_event():
    print("test_writes_one_line_per_event:")
    if os.path.exists(LOG_PATH):
        os.remove(LOG_PATH)
    ak._log_transcript("USER", "jarvis what time is it")
    ak._log_transcript("JARVIS", "The current time is 01:30:00.")
    lines = _read_log()
    ok = _check("line count", len(lines), 2)
    if ok:
        ok &= _check("line 0 role", lines[0].split(" ", 1)[1].split(":", 1)[0], "USER")
        ok &= _check("line 1 role", lines[1].split(" ", 1)[1].split(":", 1)[0], "JARVIS")
        ok &= _check("line 0 text", "jarvis what time is it" in lines[0], True)
        ok &= _check("line 1 text", "The current time is 01:30:00." in lines[1], True)
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


def run_transcript_tests() -> dict:
    print("\n[CI] TRANSCRIPT LOGGER TESTS")
    results = [
        test_writes_one_line_per_event(),
        test_iso_timestamp_format(),
        test_empty_text_silently_dropped(),
        test_thread_safe(),
        test_failure_does_not_raise(),
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
