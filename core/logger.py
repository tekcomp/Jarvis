import time

LOG_LEVEL = 3


def set_level(level: int):
    global LOG_LEVEL
    LOG_LEVEL = max(1, min(5, level))


def ts():
    return time.strftime("%H:%M:%S")


def log(level: int, msg: str):
    if LOG_LEVEL >= level:
        print(f"[{ts()}] {msg}")


def L1(msg): log(1, msg)
def L2(msg): log(2, msg)
def L3(msg): log(3, msg)
def L4(msg): log(4, msg)
def L5(msg): log(5, msg)