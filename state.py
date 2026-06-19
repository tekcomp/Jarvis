class VoiceState:
    def __init__(self):
        self.speaking = False
        self.stop_speaking = False
        self.last_user_text = ""
        self.mode = "voice"  # voice | qa

state = VoiceState()