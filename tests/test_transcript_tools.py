"""Tests for tools/transcript_to_jsonl.py and tools/transcript_filter.py.

Run: python tests/test_transcript_tools.py
"""
import json
import os
import subprocess
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
LOG = os.path.join(ROOT, "logs", "transcript.log")
OUT = os.path.join(ROOT, "data", "_test_pairs.jsonl")
TOOLS = os.path.join(ROOT, "tools")

SAMPLE = """2026-07-01T01:30:00 USER: jarvis what time is it
2026-07-01T01:30:00 [time] JARVIS: The current time is 01:30.
2026-07-01T01:31:00 USER: jarvis tell me a joke
2026-07-01T01:31:00 [joke] JARVIS: Why did the AI cross the road?
2026-07-01T01:32:00 USER: jarvis my favorite color is teal
2026-07-01T01:32:00 [llm] JARVIS: Got it, teal.
2026-07-01T01:33:00 USER: what did i just say
2026-07-01T01:33:00 [llm] JARVIS: You said your favorite color is teal.
2026-07-01T01:34:00 USER: jarvis goodbye
2026-07-01T01:34:00 [shutdown] JARVIS: Goodbye, sir.
"""


def _write_sample():
    os.makedirs(os.path.dirname(LOG), exist_ok=True)
    with open(LOG, "w", encoding="utf-8") as f:
        f.write(SAMPLE)


def _run(*args):
    return subprocess.run(
        [sys.executable, *args],
        capture_output=True, text=True, cwd=ROOT,
        env={**os.environ, "PYTHONIOENCODING": "utf-8"},
    )


def _check(name, got, expected):
    ok = got == expected
    mark = "PASS" if ok else "FAIL"
    print(f"  [{mark}] {name}: got={got!r}  expected={expected!r}")
    return ok


def test_jsonl_extract_writes_pairs():
    print("test_jsonl_extract_writes_pairs:")
    _write_sample()
    r = _run(os.path.join(TOOLS, "transcript_to_jsonl.py"), "--output", OUT)
    if r.returncode != 0:
        print(f"  [FAIL] non-zero exit: {r.returncode}\n  stderr: {r.stderr}")
        return False
    if not os.path.exists(OUT):
        print(f"  [FAIL] output file not created\n  stdout: {r.stdout}\n  stderr: {r.stderr}")
        return False
    pairs = []
    with open(OUT, "r", encoding="utf-8") as f:
        for line in f:
            pairs.append(json.loads(line))
    ok = _check("pair count", len(pairs), 5)
    if ok:
        ok &= _check("first user", pairs[0]["messages"][0]["content"], "jarvis what time is it")
        ok &= _check("first assistant", pairs[0]["messages"][1]["content"], "The current time is 01:30.")
        ok &= _check("first intent", pairs[0]["intent"], "time")
        ok &= _check("first timestamp", pairs[0]["timestamp"], "2026-07-01T01:30:00")
        ok &= _check("last user", pairs[-1]["messages"][0]["content"], "jarvis goodbye")
        ok &= _check("last assistant", pairs[-1]["messages"][1]["content"], "Goodbye, sir.")
        ok &= _check("last intent", pairs[-1]["intent"], "shutdown")
    return ok


def test_jsonl_dry_run():
    print("test_jsonl_dry_run:")
    _write_sample()
    if os.path.exists(OUT):
        os.remove(OUT)
    r = _run(os.path.join(TOOLS, "transcript_to_jsonl.py"),
             "--output", OUT, "--dry-run")
    ok = _check("exit code", r.returncode, 0)
    ok &= _check("output file should not exist", os.path.exists(OUT), False)
    ok &= _check("stdout mentions pair count", "5 pair" in r.stdout, True)
    return ok


def test_jsonl_intent_filter():
    print("test_jsonl_intent_filter:")
    _write_sample()
    r = _run(os.path.join(TOOLS, "transcript_to_jsonl.py"),
             "--output", OUT, "--intent", "llm", "--dry-run")
    ok = _check("stdout mentions 2 llm pairs", "2 pair" in r.stdout, True)
    return ok


def test_filter_count():
    print("test_filter_count:")
    _write_sample()
    r = _run(os.path.join(TOOLS, "transcript_filter.py"), "--count")
    ok = _check("matched 10 lines (5 USER + 5 JARVIS)", "matched 10 line" in r.stdout, True)
    return ok


def test_filter_user_only_since():
    print("test_filter_user_only_since:")
    _write_sample()
    r = _run(os.path.join(TOOLS, "transcript_filter.py"),
             "--user-only", "--since", "01:32")
    ok = _check("matched 3 user lines at/after 01:32", "matched 3 line" in r.stdout, True)
    ok &= _check("contains 'jarvis my favorite color'", "jarvis my favorite color" in r.stdout, True)
    return ok


def test_filter_intent_joke():
    print("test_filter_intent_joke:")
    _write_sample()
    r = _run(os.path.join(TOOLS, "transcript_filter.py"),
             "--intent", "joke", "--jarvis-only")
    ok = _check("matched 1 joke jarvis line", "matched 1 line" in r.stdout, True)
    ok &= _check("contains joke text", "cross the road" in r.stdout, True)
    return ok


def test_filter_text_substring():
    print("test_filter_text_substring:")
    _write_sample()
    r = _run(os.path.join(TOOLS, "transcript_filter.py"), "--text", "teal")
    # "teal" appears in 3 lines: "my favorite color is teal" (user), "Got it, teal." (jarvis), "your favorite color is teal" (jarvis).
    ok = _check("matched 3 teal lines", "matched 3 line" in r.stdout, True)
    return ok


def test_filter_no_results():
    print("test_filter_no_results:")
    _write_sample()
    r = _run(os.path.join(TOOLS, "transcript_filter.py"), "--text", "this-string-does-not-exist-xyz")
    ok = _check("matched 0 lines", "matched 0 line" in r.stdout, True)
    return ok


def run_transcript_tools_tests() -> dict:
    print("\n[CI] TRANSCRIPT TOOLS TESTS")
    results = [
        test_jsonl_extract_writes_pairs(),
        test_jsonl_dry_run(),
        test_jsonl_intent_filter(),
        test_filter_count(),
        test_filter_user_only_since(),
        test_filter_intent_joke(),
        test_filter_text_substring(),
        test_filter_no_results(),
    ]
    # Cleanup
    for p in (OUT, LOG):
        if os.path.exists(p):
            os.remove(p)
    passed = sum(1 for r in results if r)
    failed = sum(1 for r in results if not r)
    print(f"transcript_tools: {passed} passed / {failed} failed")
    return {"passed": passed, "failed": failed}


if __name__ == "__main__":
    res = run_transcript_tools_tests()
    sys.exit(0 if res["failed"] == 0 else 1)
