class JarvisState:
    def __init__(self):
        self.listening = True
        self.speaking = False
        self.stop_speaking = False
        self.wake_word_detected = False


# 👇 GLOBAL INSTANCE (THIS IS THE FIX)
state = JarvisState()