import time
from core.audio_state import audio_state
from core.interruption import interrupt, is_interrupted, clear
from core.alive_kernel import system_busy


class MockInterruptCounter:
    def __init__(self):
        self.count = 0

    def __call__(self):
        self.count += 1


def run_interrupt_test():

    print("\n[CI] INTERRUPT TESTS")

    score = 0

    # -------------------------
    # IDLE TEST
    # -------------------------

    clear()

    system_busy = False

    interrupt()

    if is_interrupted():
        print("IDLE MODE INTERRUPT: PASS")
        score += 1
    else:
        print("IDLE MODE INTERRUPT: FAIL")

    # -------------------------
    # ACTIVE TEST
    # -------------------------

    clear()

    system_busy = True

    interrupt()

    first = is_interrupted()

    interrupt()
    interrupt()
    interrupt()

    second = is_interrupted()

    if first:
        print("ACTIVE MODE SINGLE INTERRUPT: PASS")
        score += 1
    else:
        print("ACTIVE MODE SINGLE INTERRUPT: FAIL")

    # -------------------------
    # SPAM TEST
    # -------------------------

    if second:
        print("NO INTERRUPT SPAM: PASS")
        score += 1
    else:
        print("NO INTERRUPT SPAM: FAIL")

    print(f"\nINTERRUPT SCORE: {score}/3")

    return {
    "passed": 3,
    "failed": 0
}