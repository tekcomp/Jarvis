import time
import json
import os


class CIDashboard:

    def __init__(self):
        # MUST exist before add() is called
        self.items = {}

    # =====================================================
    # ADD MODULE SCORE
    # =====================================================
    def add(self, name, passed, failed, weight=1):

        if not hasattr(self, "items"):
            self.items = {}

        self.items[name] = {
            "passed": passed,
            "failed": failed,
            "weight": weight
        }

    # =====================================================
    # TOTAL SCORE CALCULATION
    # =====================================================
    def total_score(self):

        total_weight = 0
        weighted_score = 0

        for name, v in self.items.items():

            total = v["passed"] + v["failed"]
            if total == 0:
                continue

            ratio = v["passed"] / total
            weighted_score += ratio * v["weight"]
            total_weight += v["weight"]

        if total_weight == 0:
            return 0

        return int((weighted_score / total_weight) * 100)

    # =====================================================
    # DASHBOARD RENDER
    # =====================================================
    def render(self):

        print("\n[CI DASHBOARD]\n")

        for name, v in self.items.items():
            total = v["passed"] + v["failed"]
            print(
                f"{name.upper():10} | "
                f"{v['passed']}/{total} "
                f"| weight={v['weight']}"
            )

        print("\n")

    # =====================================================
    # EXPORT (future use)
    # =====================================================
    def export(self):
        pass