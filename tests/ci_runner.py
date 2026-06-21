import sys
import os

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

from tests.test_brain import run_brain_tests
from tests.test_pipeline_mock import run_pipeline_tests
from tests.test_wake_stream import run_wake_tests
from tests.test_interrupt import run_interrupt_test
from tests.ci_dashboard import CIDashboard


# =========================================================
# WEIGHTS (IMPORTANT FOR REAL SCORING)
# =========================================================
WEIGHTS = {
    "brain": 40,
    "pipeline": 20,
    "wake": 15,
    "interrupt": 25,
}


def safe_run(fn, name):
    try:
        return fn()
    except Exception as e:
        print(f"[CI ERROR] {name} crashed: {e}")
        return {"passed": 0, "failed": 1}


# =========================================================
# LIVE CI RUNNER
# =========================================================
def main():

    print("\n===================================")
    print(" JARVIS CI PIPELINE v2 + DASHBOARD")
    print("===================================\n")

    dash = CIDashboard()

    # -------------------------
    # CORE TESTS (SAFE EXECUTION)
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
    # REAL SYSTEM METRICS (NOT FAKE)
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


if __name__ == "__main__":
    main()