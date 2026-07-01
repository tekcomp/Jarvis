"""core/wc_intent.py

World Cup 2026 voice intent: answers queries about USA / next match / today's
matches by reading data/worldcup_2026_fixtures.json.
"""
import json
import os
from datetime import date, datetime

_FIXTURES_PATH = os.path.normpath(os.path.join(
    os.path.dirname(__file__), "..", "data", "worldcup_2026_fixtures.json"
))


def _load():
    with open(_FIXTURES_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def _parse(d):
    try:
        return date.fromisoformat(d)
    except Exception:
        return None


def _fmt(match):
    when = match.get("date", "?")
    home = match.get("homeTeam", "TBD")
    away = match.get("awayTeam", "TBD")
    city = match.get("hostCity", "").replace("-", " ")
    stadium = match.get("stadium", "")
    line = f"{when}: {home} vs {away}"
    if city:
        line += f", in {city}"
    if stadium:
        line += f", at {stadium}"
    return line + "."


def _team_matches(team, fixtures):
    t = team.lower()
    return [m for m in fixtures
            if t in (m.get("homeTeam", "")).lower()
            or t in (m.get("awayTeam", "")).lower()]


def handle_wc_intent(text: str) -> str:
    """Return a voice-friendly answer, or '' if the query is not WC-related."""
    t = text.lower()
    if "world cup" not in t and "usa" not in t and "united states" not in t:
        return ""

    data = _load()
    fixtures = data.get("fixtures", [])
    today_iso = date.today().isoformat()

    # 1. "when does USA play next"
    if "next" in t or "upcoming" in t or "when" in t:
        team = "United States" if "usa" in t or "united states" in t else None
        pool = _team_matches(team, fixtures) if team else fixtures
        future = [m for m in pool if _parse(m.get("date", "")) and _parse(m["date"]) >= date.today()]
        future.sort(key=lambda m: m.get("date", ""))
        if not future:
            return "I have no upcoming World Cup matches on record."
        return f"The next World Cup match is {_fmt(future[0])}"

    # 2. "today"
    if "today" in t or "tonight" in t:
        todays = [m for m in fixtures if m.get("date") == today_iso]
        if not todays:
            return "There are no World Cup matches today."
        if len(todays) == 1:
            return f"Today, {_fmt(todays[0])}"
        return f"Today there are {len(todays)} World Cup matches: " + "; ".join(_fmt(m) for m in todays)

    # 3. "USA's schedule / list USA matches"
    if "usa" in t or "united states" in t:
        usa = _team_matches("United States", fixtures)
        if not usa:
            return "I have no United States matches on record."
        usa.sort(key=lambda m: m.get("date", ""))
        return f"The United States play {len(usa)} matches. " + " Next: " + _fmt(usa[0])

    # 4. "what's the first match / opener"
    if "first" in t or "opener" in t or "opening" in t:
        first = sorted(fixtures, key=lambda m: m.get("date", ""))[:1]
        if first:
            return f"The opening match is {_fmt(first[0])}"

    return ""