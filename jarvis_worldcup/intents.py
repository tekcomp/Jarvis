# jarvis_worldcup/intents.py
from datetime import date
from .schedule import fixtures_for_team, fixtures_for_date, format_fixture
from jarvis_core.log_reader import read_last_logs

# Country routing for team-fixture queries.
# Each entry: (lowercase keyword(s) to match in user text, canonical team name
# as it appears in data/worldcup_2026_fixtures.json, short label for the reply).
TEAM_QUERIES = [
    (("usa", "united states", "u.s.", "u.s.a."), "United States", "USA"),
    (("mexico",), "Mexico", "Mexico"),
    (("canada",), "Canada", "Canada"),
    (("brazil",), "Brazil", "Brazil"),
    (("argentina",), "Argentina", "Argentina"),
    (("france",), "France", "France"),
    (("germany",), "Germany", "Germany"),
    (("spain",), "Spain", "Spain"),
    (("england",), "England", "England"),
    (("portugal",), "Portugal", "Portugal"),
    (("netherlands", "holland"), "Netherlands", "Netherlands"),
    (("belgium",), "Belgium", "Belgium"),
    (("japan",), "Japan", "Japan"),
    (("morocco",), "Morocco", "Morocco"),
    (("senegal",), "Senegal", "Senegal"),
    (("ghana",), "Ghana", "Ghana"),
    (("croatia",), "Croatia", "Croatia"),
    (("norway",), "Norway", "Norway"),
    (("switzerland",), "Switzerland", "Switzerland"),
    (("australia",), "Australia", "Australia"),
    (("south korea", "korea"), "South Korea", "South Korea"),
    (("saudi arabia",), "Saudi Arabia", "Saudi Arabia"),
    (("uruguay",), "Uruguay", "Uruguay"),
    (("ecuador",), "Ecuador", "Ecuador"),
    (("ivory coast", "cote d'ivoire"), "Ivory Coast", "Ivory Coast"),
    (("tunisia",), "Tunisia", "Tunisia"),
    (("egypt",), "Egypt", "Egypt"),
    (("iran",), "Iran", "Iran"),
    (("new zealand",), "New Zealand", "New Zealand"),
    (("qatar",), "Qatar", "Qatar"),
    (("haiti",), "Haiti", "Haiti"),
    (("scotland",), "Scotland", "Scotland"),
    (("paraguay",), "Paraguay", "Paraguay"),
    (("panama",), "Panama", "Panama"),
    (("jordan",), "Jordan", "Jordan"),
    (("algeria",), "Algeria", "Algeria"),
    (("austria",), "Austria", "Austria"),
    (("cabo verde", "cape verde"), "Cabo Verde", "Cabo Verde"),
    (("curaçao", "curacao"), "Curaçao", "Curaçao"),
    (("south africa",), "South Africa", "South Africa"),
]


def _find_team_query(t: str):
    """Return (canonical_name, label) for the first country whose keyword
    appears in the lowercased text, or None if no match."""
    for keywords, canonical, label in TEAM_QUERIES:
        for kw in keywords:
            if kw in t:
                return canonical, label
    return None


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

    team = _find_team_query(t)
    if team is not None:
        canonical_name, label = team
        fixtures = fixtures_for_team(canonical_name)
        if not fixtures:
            return f"{canonical_name} has no scheduled matches in this dataset."
        lines = [format_fixture(m) for m in fixtures]
        return f"Here are {label}'s World Cup matches:\n" + "\n".join(lines)

    if "today" in t:
        today = date.today()
        fixtures = fixtures_for_date(today)
        if not fixtures:
            return f"There are no World Cup matches on {today.isoformat()}."
        lines = [format_fixture(m) for m in fixtures]
        return f"Matches today ({today.isoformat()}):\n" + "\n".join(lines)

    return "I can answer questions like 'What day does USA play?' or 'What games are playing today?'."
