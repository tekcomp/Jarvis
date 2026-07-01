# tests/test_schedule_queries.py
from datetime import date
from jarvis_worldcup.schedule import fixtures_for_team, fixtures_for_date

def test_usa_has_fixtures():
    fixtures = fixtures_for_team("United States")
    assert len(fixtures) >= 1

def test_date_filter():
    # pick a known date from the JSON, e.g. 2026-06-12
    fixtures = fixtures_for_date(date(2026, 6, 12))
    assert len(fixtures) >= 1
