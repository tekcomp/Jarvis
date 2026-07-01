# jarvis_core/log_reader.py
from pathlib import Path

LOG_FILE = Path("logs/jarvis.log")

def read_last_logs(lines: int = 20) -> str:
    if not LOG_FILE.exists():
        return "No logs found."

    with LOG_FILE.open("r", encoding="utf-8") as f:
        content = f.readlines()

    tail = content[-lines:]
    return "".join(tail)
