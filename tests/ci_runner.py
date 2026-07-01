import sys
import os

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

from tests.test_brain import run_brain_tests
from tests.test_pipeline_mock import run_pipeline_tests
from tests.test_wake_stream import run_wake_tests
from tests.test_interrupt import run_interrupt_test
from tests.test_wake_and_mode import run_wake_and_mode_tests
from tests.test_llm_backend import run_llm_backend_tests
from tests.test_canned_responses import run_canned_responses_tests
from tests.test_transcript import run_transcript_tests
from tests.ci_dashboard import CIDashboard
from core.contract import handle, reset

# =========================================================
# WEIGHTS (CI CONTRACT)
# =========================================================
WEIGHTS = {
    "brain": 30,
    "pipeline": 15,
    "wake": 10,
    "interrupt": 20,
    "wake_and_mode": 5,
    "llm_backend": 10,
    "canned_responses": 5,
    "transcript": 5,
}


# =========================================================
# SAFE RUN (STRICT CONTRACT NORMALIZER)
# =========================================================
def safe_run(fn, name):
    try:
        result = fn()

        # -----------------------------
        # HARD NORMALIZATION (FIXES YOUR CRASH)
        # -----------------------------
        if isinstance(result, dict):
            passed = result.get("passed", 0)
            failed = result.get("failed", 0)
            return {"passed": passed, "failed": failed}

        # legacy tuple support (JUST IN CASE)
        if isinstance(result, tuple) and len(result) == 2:
            return {"passed": result[0], "failed": result[1]}

        print(f"[CI WARNING] {name} returned invalid format: {type(result)}")
        return {"passed": 0, "failed": 1}

    except Exception as e:
        print(f"[CI ERROR] {name} crashed: {e}")
        return {"passed": 0, "failed": 1}


# =========================================================
# MAIN CI PIPELINE
# =========================================================
def main():

    print("\n===================================")
    print(" JARVIS CI PIPELINE v2 + DASHBOARD")
    print("===================================\n")

    dash = CIDashboard()

    # -------------------------
    # CORE TESTS
    # -------------------------
    b = safe_run(run_brain_tests, "brain")
    dash.add("brain", b["passed"], b["failed"], weight=WEIGHTS["brain"])

    p = safe_run(run_pipeline_tests, "pipeline")
    dash.add("pipeline", p["passed"], p["failed"], weight=WEIGHTS["pipeline"])

    w = safe_run(run_wake_tests, "wake")
    dash.add("wake", w["passed"], w["failed"], weight=WEIGHTS["wake"])

    i = safe_run(run_interrupt_test, "interrupt")
    dash.add("interrupt", i["passed"], i["failed"], weight=WEIGHTS["interrupt"])

    wm = safe_run(run_wake_and_mode_tests, "wake_and_mode")
    dash.add("wake_and_mode", wm["passed"], wm["failed"], weight=WEIGHTS["wake_and_mode"])

    llm = safe_run(run_llm_backend_tests, "llm_backend")
    dash.add("llm_backend", llm["passed"], llm["failed"], weight=WEIGHTS["llm_backend"])

    canned = safe_run(run_canned_responses_tests, "canned_responses")
    dash.add("canned_responses", canned["passed"], canned["failed"], weight=WEIGHTS["canned_responses"])

    tx = safe_run(run_transcript_tests, "transcript")
    dash.add("transcript", tx["passed"], tx["failed"], weight=WEIGHTS["transcript"])

    # -------------------------
    # SYSTEM METRICS (PLACEHOLDERS FOR NOW)
    # -------------------------
    dash.add("latency", 0, 0, weight=5)
    dash.add("memory", 0, 0, weight=5)
    dash.add("noise", 0, 0, weight=5)

    # -------------------------
    # DASHBOARD OUTPUT
    # -------------------------
    dash.render()
    dash.export()

    total = dash.total_score()

    print(f"\n[CI RESULT] {'PASS' if total >= 80 else 'FAIL'}\n")

    sys.exit(0 if total >= 80 else 1)


def run_ci_tests() -> bool:
    """
    Returns True if ALL tests pass.

    Runs every suite in WEIGHTS (brain, pipeline, wake, interrupt,
    wake_and_mode, llm_backend, canned_responses). Each suite is
    short-circuited: if any individual suite reports a failure, the
    full run returns False immediately.
    """

    print("[CI] brain tests...")
    r = run_brain_tests()
    if r["failed"]:
        return False

    print("[CI] pipeline tests...")
    if not run_pipeline_tests():
        return False

    print("[CI] wake tests...")
    if not run_wake_tests():
        return False

    print("[CI] interrupt tests...")
    r = run_interrupt_test()
    if r["failed"]:
        return False

    print("[CI] wake_and_mode tests...")
    r = run_wake_and_mode_tests()
    if r["failed"]:
        return False

    print("[CI] llm_backend tests...")
    r = run_llm_backend_tests()
    if r["failed"]:
        return False

    print("[CI] canned_responses tests...")
    r = run_canned_responses_tests()
    if r["failed"]:
        return False

    print("[CI] transcript tests...")
    r = run_transcript_tests()
    if r["failed"]:
        return False

    return True


if __name__ == "__main__":
    result = run_ci_tests()
    print("[CI RESULT]", result)