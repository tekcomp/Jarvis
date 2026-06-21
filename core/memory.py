from collections import deque

# keeps last N exchanges
MAX_MEMORY = 10

memory = deque(maxlen=MAX_MEMORY)


def add(role: str, text: str):
    memory.append((role, text))


def get_context() -> str:
    """
    Converts memory into prompt-ready context block
    """
    return "\n".join([f"{r}: {t}" for r, t in memory])


def clear():
    memory.clear()