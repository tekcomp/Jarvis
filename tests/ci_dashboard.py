import time
import json
import os


class CIDashboard:

    def __init__(self):
        self.results = {}

    # -----------------------------------------------------
    # STORE RESULT
    # -----------------------------------------------------
    def add(self, name: str, passed: int, failed: int):
        self.results[name] = {
            "passed": passed,
            "failed": failed,
            "score": self._score(passed, failed)
        }

    # -----------------------------------------------------
    # SCORE CALCULATION
    # -----------------------------------------------------
    def _score(self, p, f):
        total = p + f
        if total == 0:
            return 0
        return round((p / total) * 100, 2)

    # -----------------------------------------------------
    # WEIGHTED SYSTEM SCORE
    # -----------------------------------------------------
    def total_score(self):

        weights = {
            "brain": 0.25,
            "pipeline": 0.25,
            "wake": 0.20,
            "latency": 0.15,
            "memory": 0.10,
            "noise": 0.05
        }

        total = 0.0

        for k, v in self.results.items():
            weight = weights.get(k, 0)
            total += v["score"] * weight

        return round(total, 2)

    # -----------------------------------------------------
    # VISUAL BAR
    # -----------------------------------------------------
    def _bar(self, score):

        filled = int(score // 10)
        empty = 10 - filled

        return "█" * filled + "░" * empty

    # -----------------------------------------------------
    # PRINT DASHBOARD
    # -----------------------------------------------------
    def render(self):

        print("\n===================================")
        print(" JARVIS CI LIVE DASHBOARD")
        print("===================================\n")

        for k, v in self.results.items():

            bar = self._bar(v["score"])

            print(f"{k.upper():10} | {bar} | {v['score']}%")

        print("\n-----------------------------------")
        print(f"TOTAL SCORE: {self.total_score()} / 100")
        print("-----------------------------------\n")

    # -----------------------------------------------------
    # EXPORT JSON (future GUI hook)
    # -----------------------------------------------------
    def export(self, path="ci_report.json"):

        data = {
            "timestamp": time.time(),
            "results": self.results,
            "total_score": self.total_score()
        }

        with open(path, "w") as f:
            json.dump(data, f, indent=4)

        print(f"[CI] REPORT EXPORTED → {path}")