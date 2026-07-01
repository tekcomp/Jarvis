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
| `canned_responses` | `test_canned_responses.py` | `data/canned_responses.json` loader, mode-switch messages, goodbye, time/date templates, missing-key fallback. | `python tests\test_canned_responses.py` |

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
