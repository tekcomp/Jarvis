import threading

class AudioLock:
    def __init__(self):
        self.lock = threading.Lock()
        self.active = False

audio_lock = AudioLock()