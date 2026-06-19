import time
import json
import numpy as np
from dataclasses import dataclass, asdict

# -----------------------------
# CONFIG
# -----------------------------

NOISE_BLOCK = {
    "you",
    "okay",
    "ok",
    "huh",
    "thanks for watching",
    "yeah"
}

MIN_WORDS = 3


# -----------------------------
# RESULT STRUCTURE
# -----------------------------

@dataclass
class TestResult:
    input: str
    output: str
    passed: bool
    reason: str
    latency_ms: float


# -----------------------------
# CORE QA ENGINE
# -----------------------------

class VoiceQA:

    def __init__(self, brain_fn):
        """
        brain_fn = process_audio or process_text function
        """
        self.brain_fn = brain_fn
        self.results = []

    # -------------------------
    # RUN SINGLE TEST
    # -------------------------
    def run_test(self, input_text: str):

        start = time.time()

        output = self._capture_output(input_text)

        latency = (time.time() - start) * 1000

        result = self._evaluate(input_text, output, latency)

        self.results.append(result)

        self._print_result(result)

    # -------------------------
    # SIMULATE BRAIN PIPELINE
    # -------------------------
    def _capture_output(self, text: str):

        captured = {"output": ""}

        # monkey patch speak to capture output instead of audio
        import tts.voice as tts

        original_speak = tts.speak

        def fake_speak(x):
            captured["output"] += str(x) + " "

        tts.speak = fake_speak

        try:
            self.brain_fn(text)
        except Exception as e:
            captured["output"] = f"ERROR: {e}"

        tts.speak = original_speak

        return captured["output"].strip().lower()

    # -------------------------
    # SCORING LOGIC
    # -------------------------
    def _evaluate(self, inp, out, latency):

        inp_l = inp.lower().strip()
        out_l = out.lower().strip()

        # noise filter test
        if inp_l in NOISE_BLOCK:
            return TestResult(inp, out, False, "Noise input should be ignored", latency)

        # too short response
        if len(out_l.split()) < 2:
            return TestResult(inp, out, False, "Too short / invalid response", latency)

        # duplicate spam detection
        if out_l.count(out_l.split()[0]) > 3:
            return TestResult(inp, out, False, "Possible repetition loop", latency)

        # default pass
        return TestResult(inp, out, True, "OK", latency)

    # -------------------------
    # PRINT RESULT
    # -------------------------
    def _print_result(self, r: TestResult):

        status = "PASS" if r.passed else "FAIL"

        print(f"\n[{status}]")
        print(f"INPUT: {r.input}")
        print(f"OUTPUT: {r.output}")
        print(f"LATENCY: {r.latency_ms:.2f} ms")
        print(f"REASON: {r.reason}")

    # -------------------------
    # SUMMARY REPORT
    # -------------------------
    def summary(self):

        total = len(self.results)
        passed = sum(1 for r in self.results if r.passed)

        avg_latency = sum(r.latency_ms for r in self.results) / total

        print("\n===== VOICE QA SUMMARY =====")
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(f"Avg Latency: {avg_latency:.2f} ms")

        return {
            "total": total,
            "passed": passed,
            "failed": total - passed,
            "avg_latency": avg_latency
        }

    # -------------------------
    # SAVE REPORT
    # -------------------------
    def save(self, path="qa_report.json"):

        with open(path, "w") as f:
            json.dump([asdict(r) for r in self.results], f, indent=2)

        print(f"\nSaved report → {path}")