# Jarvis Test Suite

Automated tests for the Jarvis voice assistant. All tests live in this
folder and are wired into a single CI entry point.

## Quick start

```powershell
# Run the full CI (all suites, with dashboard)
$env:PYTHONPATH = "."
python tests\ci_runner.py
```

A green run prints `[CI RESULT] True` and exits 0.

## Suites

| Suite | File | What it covers | Run individually |
|---|---|---|---|
| `brain` | `test_brain.py` | Real `core.brain.route_intent` on text the kernel would actually pass in (post-wake-strip). Asserts classification of time/date/joke/mode/empty. | `python tests\test_brain.py` |
| `pipeline` | `test_pipeline_mock.py` | End-to-end mock audio flow: `handle(text)` → TTS. | (called by `ci_runner`) |
| `wake` | `test_wake_stream.py` | `core.contract.handle` against bare wake-word, follow-ups, and noise. | (called by `ci_runner`) |
| `interrupt` | `test_interrupt.py` | `InterruptFSM` allowed/blocked/spam behavior. | (called by `ci_runner`) |
| `wake_and_mode` | `test_wake_and_mode.py` | Wake-strip edge cases (`jarvis jarvis mode`), contains_wake_word, bare-mode intent branch, word-boundary regression. | `python tests\test_wake_and_mode.py` |
| `llm_backend` | `test_llm_backend.py` | Mock Ollama HTTP server: streaming, payload shape (model/prompt/system/transcript), default-model sanity, network-failure fallback. | `python tests\test_llm_backend.py` |
| `canned_responses` | `test_canned_responses.py` | `data/canned_responses.json` loader, mode-switch messages, goodbye, time/date templates, missing-key fallback, version + memory self-report intents. | `python tests\test_canned_responses.py` |
| `transcript` | `test_transcript.py` | `core.alive_kernel._log_transcript` writes `logs/transcript.log` with ISO-8601 timestamps. Tests file format, intent tagging, threading, failure isolation, canned-intent classification. | `python tests\test_transcript.py` |
| `transcript_tools` | `test_transcript_tools.py` | `tools/transcript_filter.py` and `tools/transcript_to_jsonl.py` — the filter and JSONL extractor utilities. Subprocess-based integration tests. | `python tests\test_transcript_tools.py` |

The `brain` suite tests the **real** code path — previously it imported
`core.spec.spec_loader`, a parallel contract layer that is no longer the
primary implementation. The spec layer still exists for migration
purposes but the live kernel uses `core.brain` directly.

## Conventions

- Each test file exports a function `run_<suite>_tests()` that returns
  `{"passed": N, "failed": M}`. The CI runner consumes that dict.
- Tests reset `core.personality_engine_v2` and `core.brain._MEMORY`
  between cases so global state doesn't leak.
- Mock HTTP servers live inside the test files (no fixtures needed).
- The `llm_backend` test uses a real in-process `ThreadingHTTPServer`
  bound to `127.0.0.1:0` — no real Ollama call is made.

## Adding a new suite

1. Create `tests/test_<name>.py` with a `run_<name>_tests()` function
   returning `{"passed": N, "failed": M}`.
2. Add the import + a `safe_run` call + a `dash.add(...)` line in
   `tests/ci_runner.py` (both in `main()` and in `run_ci_tests()`).
3. Add a row to the **Suites** table above.
4. Add a weight to `WEIGHTS` in `ci_runner.py`. Total must stay at 100.

## Environment variables

| Var | Default | Effect |
|---|---|---|
| `JARVIS_OLLAMA_URL` | `http://127.0.0.1:11434` | Ollama endpoint. Tests can override to point at the mock server. |
| `JARVIS_OLLAMA_MODEL` | `qwen2.5-coder:14b` | Model used by `core.brain`. Verified-installed: `gemma3:latest`, `qwen2.5-coder:14b`, `phi4:14b`, `glm-4.7-flash:latest`, `llama3:latest`, `phi3.5:latest`. |
| `JARVIS_OLLAMA_TIMEOUT` | `30` | Seconds. |
| `JARVIS_MEM_TURNS` | `6` | Ring-buffer size for conversation memory. |
| `PYTHONPATH` | `.` | Must include the repo root so `from core import brain` works. |
| `PYTHONIOENCODING` | `utf-8` | Required on Windows so emojis in jokes/TTS don't crash `cp1252`. |

## Transcript log

`logs/transcript.log` is written by the live kernel every time the user
says something or Jarvis speaks. Format is one line per event:

```text
2026-07-01T01:33:43 USER: jarvis what time is it
2026-07-01T01:33:43 JARVIS: The current time is 01:30:00.
2026-07-01T01:33:43 USER: thanks
2026-07-01T01:33:44 JARVIS: You're welcome.
```

Use it to:

- See what the user actually said (vs. what you think they said)
- Audit Jarvis's replies (e.g. "did Jarvis actually answer that?")
- Build a training set for fine-tuning

Tail it in real time:

```powershell
Get-Content logs\transcript.log -Tail 20 -Wait
```

Or grep for a specific event:

```powershell
Select-String -Path logs\transcript.log -Pattern "USER:.*teal"
```

The logger is in `core.alive_kernel._log_transcript` and is wired into
both the TTS worker (writes `JARVIS:` lines) and the cognitive loop
(writes `USER:` lines). It is thread-safe and silently swallows
failures so a disk-full or permission error never crashes the kernel.

### Intent tagging

Each line can carry an optional intent tag in square brackets between
the timestamp and the role. The tag describes which layer answered:

```text
2026-07-01T01:33:43 [time]  USER: jarvis what time is it
2026-07-01T01:33:43 [time]  JARVIS: The current time is 01:33.
2026-07-01T01:33:50 [joke]  USER: jarvis tell me a joke
2026-07-01T01:33:50 [joke]  JARVIS: Why did the AI cross the road?
2026-07-01T01:34:10 [llm]   USER: write me a haiku about debugging
2026-07-01T01:34:10 [llm]   JARVIS: Code's tangled mess, ...
2026-07-01T01:34:30 [llm]   USER: my favorite color is teal
2026-07-01T01:34:30 [mode]  JARVIS: Switched to jarvis mode.    <-- mode-switch intent wins
```

Tags you'll see: `time`, `date`, `joke`, `mode`, `holiday`, `shutdown`,
`version`, `memory`, `wake_only`, `canned` (Layer-1 catch-all), and
`llm` (Layer-2 fallback).

## Tools

Two utilities live in `tools/` and operate on `logs/transcript.log`:

### `tools/transcript_filter.py`

Quick interactive query. Filters by time, intent, role, text, regex.

```powershell
# Just count today's lines
python tools\transcript_filter.py --count

# What did the user say after 01:30?
python tools\transcript_filter.py --user-only --since 01:30

# Only JARVIS joke replies
python tools\transcript_filter.py --intent joke --jarvis-only

# Substring match
python tools\transcript_filter.py --text teal
```

Defaults to the last 24 hours if no `--since` or `--last-hours` is given.

### `tools/transcript_to_jsonl.py`

Convert pairs of USER / JARVIS lines into a JSONL file for fine-tuning
(OpenAI chat format).

```powershell
# All pairs
python tools\transcript_to_jsonl.py

# Only LLM-fallback exchanges, since 14:00, max 1000 pairs
python tools\transcript_to_jsonl.py --intent llm --since 14:00 --max-pairs 1000

# Dry-run to preview
python tools\transcript_to_jsonl.py --dry-run

# Custom output path
python tools\transcript_to_jsonl.py --output data\my_pairs.jsonl
```

Output schema (one record per line):

```json
{"messages": [
    {"role": "user",      "content": "jarvis what time is it"},
    {"role": "assistant", "content": "The current time is 01:30."}
], "intent": "time", "timestamp": "2026-07-01T01:30:00"}
```

## Troubleshooting

- **`[CI ERROR] <name> crashed: <Traceback>`** — the suite raised an
  exception instead of returning a dict. Run the file directly to see
  the full traceback.
- **Unicode errors on `sys.stdout.write`** — set
  `$env:PYTHONIOENCODING = "utf-8"` before running.
- **Mock-server tests hang** — the in-process `ThreadingHTTPServer` is
  daemon-threaded; if a test exits early, the thread is cleaned up on
  process exit. If you see hangs, check the `mock_server.stop()` is
  reached in a `finally` block.
