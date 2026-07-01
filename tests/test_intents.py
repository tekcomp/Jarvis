# tests/test_intents.py
from jarvis_worldcup.intents import handle_query

def test_usa_intent():
    resp = handle_query("Jarvis, what day does USA play?")
    assert "USA's World Cup matches" in resp

def test_today_intent():
    resp = handle_query("What games are playing today?")
    # Just assert it doesn't fall back to help text
    assert "I can answer questions like" not in resp
