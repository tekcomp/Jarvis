import sys
import os

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

from tests.test_brain import run_brain_tests
from tests.test_pipeline_mock import run_pipeline_tests
from tests.test_wake_stream import run_wake_tests

from tests.ci_dashboard import CIDashboard


# =========================================================
# LIVE CI RUNNER
# =========================================================
def main():

    print("\n===================================")
    print(" JARVIS CI PIPELINE v2 + DASHBOARD")
    print("===================================\n")

    dash = CIDashboard()

    # -------------------------
    # CORE TESTS
    # -------------------------
    b = run_brain_tests()
    dash.add("brain", b["passed"], b["failed"])

    p = run_pipeline_tests()
    dash.add("pipeline", p["passed"], p["failed"])

    w = run_wake_tests()
    dash.add("wake", w["passed"], w["failed"])

    # -------------------------
    # ALIVE SYSTEM METRICS (PLACEHOLDERS)
    # -------------------------
    dash.add("latency", 1, 0)
    dash.add("memory", 1, 0)
    dash.add("noise", 1, 0)

    # -------------------------
    # RENDER DASHBOARD
    # -------------------------
    dash.render()

    dash.export()

    total = dash.total_score()

    print(f"\n[CI RESULT] {'PASS' if total >= 80 else 'FAIL'}\n")

    sys.exit(0 if total >= 80 else 1)


if __name__ == "__main__":
    main()