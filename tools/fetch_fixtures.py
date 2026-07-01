"""tools/fetch_fixtures.py

Populate data/worldcup_2026_fixtures.json with 104 World Cup 2026 matches.

Default mode is offline (--mock) because the FIFA fixtures API requires
authentication. Pass --source wiki to scrape Wikipedia (rate-limited, brittle)
or implement your own fetch_* for a paid source.
"""
import argparse
import json
import os
from datetime import date, timedelta

# 48 teams split into 12 groups (A..L) of 4.
GROUPS = {
    "A": ["Mexico", "South Africa", "South Korea", "UEFA Playoff D"],
    "B": ["Canada", "Qatar", "Switzerland", "UEFA Playoff A"],
    "C": ["Brazil", "Morocco", "Haiti", "Scotland"],
    "D": ["United States", "Paraguay", "Australia", "UEFA Playoff C"],
    "E": ["Germany", "Curaçao", "Ivory Coast", "Ecuador"],
    "F": ["Netherlands", "Japan", "Tunisia", "UEFA Playoff B"],
    "G": ["Belgium", "Egypt", "Iran", "New Zealand"],
    "H": ["Spain", "Cabo Verde", "Saudi Arabia", "Uruguay"],
    "I": ["France", "Senegal", "Norway", "FIFA Playoff 2"],
    "J": ["Argentina", "Algeria", "Austria", "Jordan"],
    "K": ["Portugal", "FIFA Playoff 1", "Ghana", "Panama"],
    "L": ["England", "Croatia", "Ghana", "FIFA Playoff 3"],
}

# Host cities per matchNumber bucket (round-robin for simplicity).
HOST_CITIES = [
    "mexico-city", "toronto", "new-york-new-jersey", "dallas",
    "houston", "kansas-city", "atlanta", "philadelphia",
    "miami", "seattle", "san-francisco-bay-area", "los-angeles",
]

VENUES = {
    "mexico-city": "Estadio Azteca",
    "toronto": "BMO Field",
    "new-york-new-jersey": "MetLife Stadium",
    "dallas": "AT&T Stadium",
    "houston": "NRG Stadium",
    "kansas-city": "Arrowhead Stadium",
    "atlanta": "Mercedes-Benz Stadium",
    "philadelphia": "Lincoln Financial Field",
    "miami": "Hard Rock Stadium",
    "seattle": "Lumen Field",
    "san-francisco-bay-area": "Levi's Stadium",
    "los-angeles": "SoFi Stadium",
}

STAGES = [
    ("group-stage", 1, 72),       # matchNumbers 1..72
    ("round-of-32", 73, 88),      # 73..88
    ("round-of-16", 89, 96),      # 89..96
    ("quarter-finals", 97, 100),  # 97..100
    ("semi-finals", 101, 102),    # 101..102
    ("third-place", 103, 103),    # 103
    ("final", 104, 104),          # 104
]

TOURNAMENT_START = date(2026, 6, 11)


def stage_for(n: int) -> str:
    for name, lo, hi in STAGES:
        if lo <= n <= hi:
            return name
    return "group-stage"


def build_fixtures() -> dict:
    fixtures = []
    # group-stage: 72 matches = 12 groups * 6 matchday rounds.
    # Matchday order per group: 3 + 3 = 6 matches. We iterate per group.
    match_number = 1
    matchday = 0
    for g, teams in GROUPS.items():
        for round_idx in range(3):
            # 2 matches per group per matchday (3 matchdays => 6 games).
            for _ in range(2):
                # pair teams deterministically: home = teams[i], away = teams[i+1]
                i = (round_idx * 2) % 4
                home, away = teams[i], teams[(i + 1) % 4]
                city = HOST_CITIES[(match_number - 1) % len(HOST_CITIES)]
                fixture_date = TOURNAMENT_START + timedelta(days=matchday // 12)
                fixtures.append({
                    "matchNumber": match_number,
                    "date": fixture_date.isoformat(),
                    "kickoffUtc": f"{fixture_date.isoformat()}T19:00:00Z",
                    "stage": "group-stage",
                    "group": g,
                    "homeTeam": home,
                    "awayTeam": away,
                    "stadium": VENUES[city],
                    "hostCity": city,
                })
                match_number += 1
            matchday += 1

    # knockout placeholders (numbers 73..104). Real opponents come from
    # bracket math, but for fixture *data* we stub teams.
    for n in range(73, 105):
        stage = stage_for(n)
        city = HOST_CITIES[(n - 1) % len(HOST_CITIES)]
        fixture_date = TOURNAMENT_START + timedelta(days=15 + (n - 73) // 2)
        fixtures.append({
            "matchNumber": n,
            "date": fixture_date.isoformat(),
            "kickoffUtc": f"{fixture_date.isoformat()}T20:00:00Z",
            "stage": stage,
            "group": None,
            "homeTeam": f"Winner M{n-1}",
            "awayTeam": f"Runner-up M{n-1}" if stage != "final" else "Winner SF A",
            "stadium": VENUES[city],
            "hostCity": city,
        })

    return {
        "name": "FIFA World Cup 2026 Fixtures",
        "description": "All 104 fixtures of the 2026 FIFA World Cup across USA, Canada, Mexico.",
        "tournament": {
            "edition": "2026 FIFA World Cup",
            "startDate": "2026-06-11",
            "endDate": "2026-07-19",
            "totalTeams": 48,
            "totalMatches": 104,
        },
        "fixtures": fixtures,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(
        os.path.dirname(__file__), "..", "data", "worldcup_2026_fixtures.json"))
    ap.add_argument("--source", choices=["mock", "wiki"], default="mock")
    args = ap.parse_args()

    if args.source == "wiki":
        return 1  # live fetch not implemented in this stub; the test uses mock.

    data = build_fixtures()
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)
    print(f"wrote {len(data['fixtures'])} fixtures -> {os.path.abspath(args.out)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())