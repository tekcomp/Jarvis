class JarvisState:
    def __init__(self):
        self.listening = True
        self.speaking = False
        self.stop_speaking = False
        self.wake = False

state = JarvisState()