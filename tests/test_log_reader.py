# tests/test_log_reader.py
from jarvis_core.log_reader import read_last_logs

def test_read_logs():
    logs = read_last_logs(5)
    assert isinstance(logs, str)
