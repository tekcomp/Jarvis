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

    clear()

    counter = MockInterruptCounter()

    # monkey patch interrupt function
    import core.interruption as ic
    ic.interrupt = counter

    # =================================================
    # TEST 1: IDLE MODE (should NOT interrupt)
    # =================================================
    system_busy.clear()

    counter.count = 0

    if system_busy.is_set():
        print("FAIL: system_busy should be false")

    # simulate vad trigger
    if system_busy.is_set():
        interrupt()

    time.sleep(0.1)

    test1 = counter.count == 0
    print(f"IDLE MODE INTERRUPT: {'PASS' if test1 else 'FAIL'}")

    # =================================================
    # TEST 2: ACTIVE SPEECH MODE (should interrupt ONCE)
    # =================================================
    system_busy.set()

    counter.count = 0

    # simulate 10 rapid frames
    for _ in range(10):
        if system_busy.is_set():
            interrupt()
        time.sleep(0.01)

    test2 = counter.count == 1

    print(f"ACTIVE MODE SINGLE INTERRUPT: {'PASS' if test2 else 'FAIL'}")

    # =================================================
    # TEST 3: NO SPAM
    # =================================================
    system_busy.set()

    counter.count = 0

    for _ in range(50):
        if system_busy.is_set():
            interrupt()

    test3 = counter.count == 1

    print(f"NO INTERRUPT SPAM: {'PASS' if test3 else 'FAIL'}")

    total = test1 + test2 + test3

    print(f"\nINTERRUPT SCORE: {total}/3")

    return {"passed": total, "failed": 3 - total}