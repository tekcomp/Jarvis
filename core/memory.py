# core/memory.py
from collections import deque
from datetime import datetime

# =========================================================
# SIMPLE IN-MEMORY CONTEXT BUFFER (NO DATABASE YET)
# =========================================================

MAX_MEMORY = 50

_memory = deque(maxlen=MAX_MEMORY)


def add(role: str, text: str):
    """
    Store conversation turn
    role: 'user' | 'assistant'
    """
    _memory.append({
        "role": role,
        "text": text,
        "time": datetime.now().isoformat()
    })


def get_context(limit: int = 10):
    """
    Return last N messages for context injection later
    """
    return list(_memory)[-limit:]


def clear():
    _memory.clear()