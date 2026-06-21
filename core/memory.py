
# =========================================================
# SIMPLE IN-MEMORY CONTEXT BUFFER (NO DATABASE YET)
# =========================================================

from collections import deque

class WorkingMemory:
    def __init__(self, size=10):
        self.buffer = deque(maxlen=size)

    def add(self, item):
        self.buffer.append(item)

    def get_all(self):
        return list(self.buffer)