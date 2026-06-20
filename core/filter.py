import time

last_outputs = []
BLOCK_TIME = 4  # seconds


def is_echo(text: str):
    now = time.time()

    # clean old entries
    global last_outputs
    last_outputs = [(t, ts) for t, ts in last_outputs if now - ts < BLOCK_TIME]

    for t, _ in last_outputs:
        if t == text:
            return True

    return False


def mark_output(text: str):
    last_outputs.append((text, time.time()))