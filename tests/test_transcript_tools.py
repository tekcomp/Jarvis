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
2026-07-01T01:32:30 RATING: +1 great answer
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


def test_jsonl_split_by_intent():
    print("test_jsonl_split_by_intent:")
    _write_sample()
    stem = os.path.splitext(OUT)[0]
    r = _run(os.path.join(TOOLS, "transcript_to_jsonl.py"),
             "--output", OUT, "--split-by-intent")
    if r.returncode != 0:
        print(f"  [FAIL] non-zero exit: {r.returncode}\n  stderr: {r.stderr}")
        return False
    # Expect 4 intent files: time, joke, llm, shutdown (no untagged in sample).
    expected = {
        "time": 1,
        "joke": 1,
        "llm": 2,
        "shutdown": 1,
    }
    ok = True
    for intent, count in expected.items():
        path = f"{stem}__{intent}.jsonl"
        if not os.path.exists(path):
            print(f"  [FAIL] expected output file {path} not created")
            ok = False
            continue
        with open(path, "r", encoding="utf-8") as f:
            lines = [l for l in f if l.strip()]
        ok &= _check(f"{intent} file pair count", len(lines), count)
    # The single combined file should NOT exist when --split-by-intent is on.
    ok &= _check("combined file should not exist", os.path.exists(OUT), False)
    # Cleanup the per-intent files
    for intent in expected:
        path = f"{stem}__{intent}.jsonl"
        if os.path.exists(path):
            os.remove(path)
    return ok


def test_jsonl_rating_attached():
    print("test_jsonl_rating_attached:")
    _write_sample()
    r = _run(os.path.join(TOOLS, "transcript_to_jsonl.py"), "--output", OUT)
    if r.returncode != 0:
        print(f"  [FAIL] non-zero exit: {r.returncode}\n  stderr: {r.stderr}")
        return False
    with open(OUT, "r", encoding="utf-8") as f:
        pairs = [json.loads(l) for l in f if l.strip()]
    # The RATING: +1 line at 01:32:30 comes right after the "Got it, teal."
    # JARVIS line. The rating should attach to that JARVIS line's pair
    # (the one where the user said "my favorite color is teal" and Jarvis
    # said "Got it, teal.")
    teal_pair = next(
        (p for p in pairs if "Got it, teal" in p["messages"][1]["content"]),
        None,
    )
    if teal_pair is None:
        print("  [FAIL] could not find the 'Got it, teal' pair")
        return False
    ok = _check("rating attached to prior JARVIS line", teal_pair.get("rating"), 1)
    return ok


def test_jsonl_min_rating_filter():
    print("test_jsonl_min_rating_filter:")
    _write_sample()
    r = _run(os.path.join(TOOLS, "transcript_to_jsonl.py"),
             "--output", OUT, "--min-rating", "1")
    if r.returncode != 0:
        print(f"  [FAIL] non-zero exit: {r.returncode}\n  stderr: {r.stderr}")
        return False
    with open(OUT, "r", encoding="utf-8") as f:
        pairs = [json.loads(l) for l in f if l.strip()]
    # 1 pair has rating=+1 in our sample (the teal-recall), so output is 1.
    return _check("only rated-up pair kept", len(pairs), 1)


def test_rate_jarvis_appends_line():
    print("test_rate_jarvis_appends_line:")
    _write_sample()
    r = _run(os.path.join(TOOLS, "rate_jarvis.py"), "--value", "1", "--comment", "test")
    if r.returncode != 0:
        print(f"  [FAIL] non-zero exit: {r.returncode}\n  stderr: {r.stderr}")
        return False
    with open(LOG, "r", encoding="utf-8") as f:
        content = f.read()
    ok = _check("rating line appended", content.count("RATING: +1 test"), 1)
    ok &= _check("stdout reports success", "thumbs up" in r.stdout, True)
    return ok


def test_rate_jarvis_invalid_value():
    print("test_rate_jarvis_invalid_value:")
    _write_sample()
    r = _run(os.path.join(TOOLS, "rate_jarvis.py"), "--value", "5")
    ok = _check("non-zero exit", r.returncode != 0, True)
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
        test_jsonl_split_by_intent(),
        test_jsonl_rating_attached(),
        test_jsonl_min_rating_filter(),
        test_rate_jarvis_appends_line(),
        test_rate_jarvis_invalid_value(),
    ]
    # Cleanup
    for p in (OUT, LOG):
        if os.path.exists(p):
            os.remove(p)
    # Also clean up any leftover per-intent files.
    data_dir = os.path.join(ROOT, "data")
    if os.path.isdir(data_dir):
        for f in os.listdir(data_dir):
            if f.startswith("_test_pairs__") and f.endswith(".jsonl"):
                os.remove(os.path.join(data_dir, f))
    passed = sum(1 for r in results if r)
    failed = sum(1 for r in results if not r)
    print(f"transcript_tools: {passed} passed / {failed} failed")
    return {"passed": passed, "failed": failed}


if __name__ == "__main__":
    res = run_transcript_tools_tests()
    sys.exit(0 if res["failed"] == 0 else 1)
