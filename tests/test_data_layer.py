# tests/test_data_layer.py
from pathlib import Path
import json

def test_fixtures_file_exists():
    path = Path("data/worldcup_2026_fixtures.json")
    assert path.exists()

def test_total_matches_104():
    with Path("data/worldcup_2026_fixtures.json").open() as f:
        data = json.load(f)
    assert len(data["fixtures"]) == 104
