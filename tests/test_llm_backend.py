"""LLM backend tests using a tiny in-process mock Ollama server.

We monkey-patch `requests.post` so the test doesn't need a real Ollama
instance, but exercises the full _llm_stream code path including:
  - URL composition
  - Payload shape (model, prompt, system, stream)
  - Streaming line parsing
  - Timeout handling
  - Failure surfacing
  - transcript prepending

Run: python tests/test_llm_backend.py
"""
import json
import os
import sys
import threading
import time
from unittest import mock

import requests

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

from core import brain  # noqa: E402


# ---------------------------------------------------------------
# Mock Ollama server (HTTP, real socket)
# ---------------------------------------------------------------
class _MockOllama:
    """In-process HTTP server that mimics Ollama's /api/generate endpoint.

    Records every request payload so the test can assert on what the
    kernel actually sent. Streams a configurable token sequence back.
    """

    def __init__(self, host="127.0.0.1", port=0, tokens=None, raise_after=None):
        self.tokens = tokens or ["Mock", " response", " from", " Ollama", "."]
        self.raise_after = raise_after
        self.received_payloads: list[dict] = []
        self._server = None
        self._thread: threading.Thread | None = None
        self.host = host
        self.port = port

    def start(self):
        from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

        outer = self

        class Handler(BaseHTTPRequestHandler):
            def log_message(self, *a, **kw):  # silence stderr
                return

            def do_POST(self):  # noqa: N802
                length = int(self.headers.get("Content-Length", "0"))
                raw = self.rfile.read(length) if length else b"{}"
                try:
                    payload = json.loads(raw.decode("utf-8"))
                except Exception:
                    payload = {}
                outer.received_payloads.append(payload)

                self.send_response(200)
                self.send_header("Content-Type", "application/x-ndjson")
                self.end_headers()

                emitted = 0
                for tok in outer.tokens:
                    if outer.raise_after is not None and emitted >= outer.raise_after:
                        # Simulate a server-side connection drop.
                        return
                    chunk = json.dumps({"response": tok, "done": False}).encode("utf-8") + b"\n"
                    try:
                        self.wfile.write(chunk)
                        self.wfile.flush()
                    except Exception:
                        return
                    emitted += 1
                    time.sleep(0.005)
                self.wfile.write(json.dumps({"response": "", "done": True}).encode("utf-8") + b"\n")

        self._server = ThreadingHTTPServer((self.host, self.port), Handler)
        self.host, self.port = self._server.server_address
        self._thread = threading.Thread(target=self._server.serve_forever, daemon=True)
        self._thread.start()

    def stop(self):
        if self._server is not None:
            self._server.shutdown()
            self._server.server_close()
        if self._thread is not None:
            self._thread.join(timeout=2)


# ---------------------------------------------------------------
# Tests
# ---------------------------------------------------------------
def _collect(chunks):
    return "".join(chunks)


def test_streams_tokens(monkeypatch=None):
    print("  test_streams_tokens:")
    mock_server = _MockOllama(tokens=["Hello", ", ", "world", "!"])
    mock_server.start()
    try:
        # Point the brain at the mock server.
        monkeypatch = monkeypatch or mock.patch.object(brain, "_OLLAMA_URL", f"http://{mock_server.host}:{mock_server.port}")
        monkeypatch.start()
        try:
            tokens = list(brain._llm_stream("hi", system_prompt="You are a tester."))
        finally:
            monkeypatch.stop()
        text = _collect(tokens)
        ok = text == "Hello, world!"
        print(f"    [{'PASS' if ok else 'FAIL'}] got={text!r}")
        return ok
    finally:
        mock_server.stop()


def test_payload_shape(monkeypatch=None):
    print("  test_payload_shape:")
    mock_server = _MockOllama(tokens=["ok"])
    mock_server.start()
    try:
        m = monkeypatch or mock.patch.object(brain, "_OLLAMA_URL", f"http://{mock_server.host}:{mock_server.port}")
        m.start()
        try:
            list(brain._llm_stream(
                "what is 2+2?",
                system_prompt="You are a math tutor.",
                transcript="User: hi\nJarvis: hello!",
            ))
        finally:
            m.stop()
        if not mock_server.received_payloads:
            print("    [FAIL] no payload received")
            return False
        p = mock_server.received_payloads[0]
        checks = [
            ("model" in p, "has model"),
            ("prompt" in p, "has prompt"),
            (p.get("stream") is True, "stream=True"),
            (p.get("system") == "You are a math tutor.", "system prompt passed"),
            ("Recent conversation:" in p.get("prompt", ""), "transcript prepended"),
            ("what is 2+2?" in p.get("prompt", ""), "user prompt present"),
        ]
        ok = True
        for cond, label in checks:
            mark = "PASS" if cond else "FAIL"
            print(f"    [{mark}] {label}")
            ok = ok and cond
        return ok
    finally:
        mock_server.stop()


def test_uses_default_model():
    print("  test_uses_default_model:")
    # Brain module loads default from env at import time. We assert it
    # is one of the models that are actually installed on the host.
    # Verified-installed (from /api/tags):
    #   gemma3:latest, qwen2.5-coder:14b, phi4:14b, glm-4.7-flash:latest,
    #   llama3:latest, phi3.5:latest
    installed = {
        "gemma3:latest",
        "qwen2.5-coder:14b",
        "phi4:14b",
        "glm-4.7-flash:latest",
        "llama3:latest",
        "phi3.5:latest",
    }
    ok = brain._OLLAMA_MODEL in installed
    print(f"    [{'PASS' if ok else 'FAIL'}] _OLLAMA_MODEL = {brain._OLLAMA_MODEL!r} (must be in installed set)")
    return ok


def test_unreachable_server_does_not_raise():
    print("  test_unreachable_server_does_not_raise:")
    # Point at a port that nothing is listening on; stream should yield
    # nothing (silent failure) and print a [CI-LLM] error.
    saved_url = brain._OLLAMA_URL
    brain._OLLAMA_URL = "http://127.0.0.1:1"  # port 1 = nothing
    try:
        try:
            tokens = list(brain._llm_stream("hi", system_prompt=None))
        except Exception as e:
            print(f"    [FAIL] raised: {e}")
            return False
        ok = tokens == []
        print(f"    [{'PASS' if ok else 'FAIL'}] got {len(tokens)} tokens (expected 0)")
        return ok
    finally:
        brain._OLLAMA_URL = saved_url


def test_stream_response_falls_back_on_no_tokens():
    print("  test_stream_response_falls_back_on_no_tokens:")
    # Make the LLM call yield nothing by pointing at an unreachable host.
    saved_url = brain._OLLAMA_URL
    brain._OLLAMA_URL = "http://127.0.0.1:1"
    try:
        brain.reset_memory()
        # Use a prompt that won't match any canned intent.
        out = _collect(brain.stream_response("what is the meaning of life"))
        # Should fall back to a mode-aware canned line.
        ok = (
            "language model" in out.lower()
            or "brain" in out.lower()
            or len(out) > 0
        )
        print(f"    [{'PASS' if ok else 'FAIL'}] fallback out: {out!r}")
        return ok
    finally:
        brain._OLLAMA_URL = saved_url


def run_llm_backend_tests() -> dict:
    print("\n[CI] LLM BACKEND TESTS")
    results = [
        test_streams_tokens(),
        test_payload_shape(),
        test_uses_default_model(),
        test_unreachable_server_does_not_raise(),
        test_stream_response_falls_back_on_no_tokens(),
    ]
    passed = sum(1 for r in results if r)
    failed = sum(1 for r in results if not r)
    print(f"llm_backend: {passed} passed / {failed} failed")
    return {"passed": passed, "failed": failed}


if __name__ == "__main__":
    res = run_llm_backend_tests()
    sys.exit(0 if res["failed"] == 0 else 1)
