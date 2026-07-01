# tests/test_intent_logs.py
from jarvis_worldcup.intents import handle_query

def test_show_logs_intent():
    resp = handle_query("Jarvis show logs")
    assert "Here are the latest Jarvis logs" in resp

def test_show_errors_intent():
    resp = handle_query("Jarvis show errors")
    assert "Here are the latest errors" in resp 
    