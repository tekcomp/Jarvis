# jarvis_worldcup/schedule.py
import json
from datetime import date, datetime
from pathlib import Path
from typing import List, Dict

DATA_PATH = Path("data/worldcup_2026_fixtures.json")

def load_fixtures() -> List[Dict]:
    with DATA_PATH.open("r", encoding="utf-8") as f:
        data = json.load(f)
    return data["fixtures"]

def fixtures_for_team(team_name: str) -> List[Dict]:
    fixtures = load_fixtures()
    team_name_lower = team_name.lower()
    return [
        m for m in fixtures
        if m["homeTeam"].lower() == team_name_lower
        or m["awayTeam"].lower() == team_name_lower
    ]

def fixtures_for_date(target_date: date) -> List[Dict]:
    fixtures = load_fixtures()
    return [m for m in fixtures if m["date"] == target_date.isoformat()]

def format_fixture(m: Dict) -> str:
    return (
        f"Match {m['matchNumber']}: "
        f"{m['homeTeam']} vs {m['awayTeam']} "
        f"on {m['date']} at {m['stadium']} in {m['hostCity']}"
    )
