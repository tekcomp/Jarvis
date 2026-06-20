class VoiceState:
    def __init__(self):
        self.speaking = False
        self.ignore_audio = False

        self.last_text = ""
        self.last_processed = ""

        self.cooldown = False


state = VoiceState()