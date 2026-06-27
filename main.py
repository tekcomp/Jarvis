import os
import time
import logging
import threading
import traceback

# ============================================================
#   JARVIS VOICE ASSISTANT (FINAL VERSION)
#   Graceful Shutdown + Logging + Clean Thread Exit
# ============================================================

LOG_FILE = "voice_assistant.log"

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

logging.info("=== Jarvis Voice Assistant Started ===")

# ------------------------------------------------------------
# Shutdown Flag Helpers
# ------------------------------------------------------------
SHUTDOWN_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "shutdown.flag")

def should_shutdown():
    return os.path.exists(SHUTDOWN_PATH)

def clear_shutdown_flag():
    try:
        os.remove(SHUTDOWN_PATH)
    except FileNotFoundError:
        pass

def clear_shutdown_flag():
    try:
        os.remove("shutdown.flag")
    except FileNotFoundError:
        pass

# ------------------------------------------------------------
# Voice Assistant Thread
# ------------------------------------------------------------
class VoiceAssistant(threading.Thread):
    def __init__(self):
        super().__init__(daemon=True)
        self.running = True

    def run(self):
        logging.info("Voice assistant thread started")

        while self.running:
            # Graceful shutdown from PowerShell
            if should_shutdown():
                logging.info("Shutdown flag detected — exiting voice assistant")
                clear_shutdown_flag()
                break

            # Your voice loop goes here
            # (STT → LLM → TTS)
            time.sleep(0.1)

        logging.info("Voice assistant thread stopped cleanly")

# ------------------------------------------------------------
# Main Program
# ------------------------------------------------------------
def main():
    assistant = VoiceAssistant()
    assistant.start()

    try:
        while assistant.is_alive():
            if should_shutdown():
                logging.info("Main loop detected shutdown flag")
                assistant.running = False
                clear_shutdown_flag()
                break

            time.sleep(0.1)

    except KeyboardInterrupt:
        logging.info("KeyboardInterrupt — shutting down")
        assistant.running = False

    assistant.join()
    logging.info("=== Jarvis Voice Assistant Exited ===")

if __name__ == "__main__":
    main()
