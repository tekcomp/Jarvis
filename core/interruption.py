import threading

_interrupt = threading.Event()


def interrupt():
    _interrupt.set()


def clear():
    _interrupt.clear()


def is_interrupted():
    return _interrupt.is_set()