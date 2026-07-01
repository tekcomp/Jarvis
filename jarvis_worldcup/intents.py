# jarvis_worldcup/intents.py
from datetime import date
from .schedule import fixtures_for_team, fixtures_for_date, format_fixture
from jarvis_core.log_reader import read_last_logs

def handle_query(text: str) -> str:
    t = text.lower().strip()

    if "show logs" in t or "jarvis logs" in t or "read logs" in t:
        logs = read_last_logs(20)
        return "Here are the latest Jarvis logs:\n" + logs

    if "errors" in t and "logs" in t:
        logs = read_last_logs(20)
        error_lines = [line for line in logs.split("\n") if "[ERROR]" in line]
        if not error_lines:
            return "There are no recent errors."
        return "Here are the latest errors:\n" + "\n".join(error_lines)

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
