# tests/test_voice_stub.py
from jarvis_worldcup.intents import handle_query

def test_text_flow():
    query = "Jarvis, what day does USA play?"
    resp = handle_query(query)
    assert "USA's World Cup matches" in resp
