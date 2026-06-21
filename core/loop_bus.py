from queue import Queue

# Speech pipeline (VAD → STT)
speech_queue = Queue()

# Response pipeline (Brain → TTS)
tts_queue = Queue()