import sys
import os

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

from tests.test_brain import run_brain_tests
from tests.test_pipeline_mock import run_pipeline_tests
from tests.test_wake_stream import run_wake_tests
from tests.test_interrupt import run_interrupt_test
from tests.ci_dashboard import CIDashboard
from core.contract import handle, reset

# =========================================================
# WEIGHTS (CI CONTRACT)
# =========================================================
WEIGHTS = {
    "brain": 40,
    "pipeline": 20,
    "wake": 15,
    "interrupt": 25,
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
    """

    print("[CI] pipeline tests...")
    if not run_pipeline_tests():
        return False

    print("[CI] wake tests...")
    if not run_wake_tests():
        return False

    print("[CI] interrupt tests...")
    if not run_interrupt_test():
        return False

    return True


if __name__ == "__main__":
    result = run_ci_tests()
    print("[CI RESULT]", result)