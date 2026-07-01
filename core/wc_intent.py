"""core/wc_intent.py

World Cup 2026 voice intent: answers queries about USA / next match / today's
matches by reading data/worldcup_2026_fixtures.json.
"""
import json
import os
from datetime import date

_FIXTURES_PATH = os.path.normpath(os.path.join(
    os.path.dirname(__file__), "..", "data", "worldcup_2026_fixtures.json"
))

# Voice-friendly month names so we don't read "2026-06-12" aloud.
_MONTHS = ["", "January", "February", "March", "April", "May", "June",
           "July", "August", "September", "October", "November", "December"]

# Words that indicate a World Cup question. Without at least one (combined
# with a USA mention), the handler returns '' so unrelated "USA" mentions
# don't get WC answers.
_WC_KEYWORDS = (
    "world cup", "match", "play", "playing", "schedule", "game",
    "fixture", "opener", "opening", "today", "tonight",
    "next", "upcoming", "when", "first",
)


def _load():
    with open(_FIXTURES_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def _parse(d):
    try:
        return date.fromisoformat(d)
    except Exception:
        return None


def _fmt_date(d):
    if d is None:
        return "a date to be announced"
    return f"{_MONTHS[d.month]} {d.day}"


def _fmt(match):
    d = _parse(match.get("date", ""))
    when = _fmt_date(d)
    home = match.get("homeTeam", "TBD")
    away = match.get("awayTeam", "TBD")
    city = (match.get("hostCity") or "").replace("-", " ")
    stadium = match.get("stadium", "")
    line = f"{when}: {home} versus {away}"
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


def _looks_like_wc_question(t):
    """'world cup' is a strong signal. 'usa'/'united states' alone is not;
    require at least one WC keyword to fire."""
    if "world cup" in t:
        return True
    if "usa" in t or "united states" in t:
        return any(k in t for k in _WC_KEYWORDS)
    return False


def handle_wc_intent(text):
    """Return a voice-friendly answer, or '' if the query is not WC-related."""
    t = text.lower().strip()
    if not _looks_like_wc_question(t):
        return ""

    try:
        data = _load()
    except FileNotFoundError:
        return "I don't have the World Cup schedule loaded yet."
    except Exception as e:
        print(f"[CI-WC] load error: {e}")
        return ""

    fixtures = data.get("fixtures", [])
    if not fixtures:
        return "I don't have any World Cup fixtures loaded yet."

    # If the schedule is incomplete (<72 group-stage matches), warn the user
    # but still answer from whatever we have.
    schedule_loaded = len(fixtures) >= 72
    today_iso = date.today().isoformat()

    # 1. "when does USA play next" / "next match"
    if "next" in t or "upcoming" in t or "when" in t:
        team = "United States" if "usa" in t or "united states" in t else None
        pool = _team_matches(team, fixtures) if team else fixtures
        future = [m for m in pool
                  if _parse(m.get("date", "")) and _parse(m["date"]) >= date.today()]
        future.sort(key=lambda m: m.get("date", ""))
        if not future:
            return "I have no upcoming World Cup matches on record."
        prefix = "The United States' next match is " if team else "The next World Cup match is "
        return prefix + _fmt(future[0])

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
        head = f"The United States play {len(usa)} matches. "
        if not schedule_loaded:
            head += "Note: the schedule is only partially loaded. "
        return head + "Next: " + _fmt(usa[0])

    # 4. "what's the first match / opener"
    if "first" in t or "opener" in t or "opening" in t:
        future = [m for m in fixtures if _parse(m.get("date", ""))]
        if not future:
            return "I have no opening match on record."
        future.sort(key=lambda m: m.get("date", ""))
        return f"The opening match is {_fmt(future[0])}"

    return ""