"""tests/test_fetch_fixtures.py

Smoke test for tools/fetch_fixtures.py: writes a fixtures file, asserts the
spec's invariants (104 matches, at least one USA fixture).
"""
import json
import os
import subprocess
import sys

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
OUT_PATH = os.path.join(REPO_ROOT, "data", "worldcup_2026_fixtures.json")


def test_fixtures_file_exists():
    assert os.path.exists(OUT_PATH), f"missing fixtures file: {OUT_PATH}"


def test_total_matches_is_104():
    with open(OUT_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data["tournament"]["totalMatches"] == 104
    assert len(data["fixtures"]) == 104


def test_at_least_one_united_states_fixture():
    with open(OUT_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    usa = [m for m in data["fixtures"]
           if m.get("homeTeam") == "United States" or m.get("awayTeam") == "United States"]
    assert len(usa) >= 1, "no fixture for United States"


def test_fetch_script_runs_and_writes_file():
    """Runs tools/fetch_fixtures.py to confirm it produces a valid file end-to-end."""
    result = subprocess.run(
        [sys.executable, os.path.join(REPO_ROOT, "tools", "fetch_fixtures.py")],
        capture_output=True, text=True, check=False,
    )
    assert result.returncode == 0, f"script failed: {result.stderr}"
    assert os.path.exists(OUT_PATH)
    with open(OUT_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data["tournament"]["totalMatches"] == 104