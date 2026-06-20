class VoiceState:
    def __init__(self):
        self.speaking = False
        self.stop_speaking = False

        # 🔥 input tracking
        self.last_user_text = ""

        # 🔥 SINGLE SOURCE OF TRUTH
        self.last_text = ""

        # 🔥 processed tracking (FIX FOR YOUR ERROR)
        self.last_processed_text = ""

        # optional control flags
        self.ignore_audio = False
        self.mode = "voice"  # voice | qa


state = VoiceState()