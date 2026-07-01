# jarvis_worldcup/intents.py
from datetime import date
from .schedule import fixtures_for_team, fixtures_for_date, format_fixture

def handle_query(text: str) -> str:
    t = text.lower().strip()

    if "usa" in t or "united states" in t:
        fixtures = fixtures_for_team("United States")
        if not fixtures:
            return "The United States has no scheduled matches in this dataset."
        lines = [format_fixture(m) for m in fixtures]
        return "Here are USA's World Cup matches:\n" + "\n".join(lines)

    if "today" in t:
        today = date.today()
        fixtures = fixtures_for_date(today)
        if not fixtures:
            return f"There are no World Cup matches on {today.isoformat()}."
        lines = [format_fixture(m) for m in fixtures]
        return f"Matches today ({today.isoformat()}):\n" + "\n".join(lines)

    return "I can answer questions like 'What day does USA play?' or 'What games are playing today?'."
