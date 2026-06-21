import asyncio
import edge_tts
import threading
import queue
import pygame
import tempfile
import os

from core.audio_state import audio_state

# =========================
# INIT AUDIO PLAYER
# =========================
pygame.mixer.init()

# =========================
# SPEECH QUEUE
# =========================
speech_queue = queue.Queue()
running = True


# =========================
# EDGE TTS STREAM FUNCTION
# =========================
async def _generate_audio(text: str, path: str):
    communicate = edge_tts.Communicate(text, "en-US-AriaNeural")
    await communicate.save(path)


# =========================
# WORKER THREAD (SINGLE VOICE ENGINE)
# =========================
def _tts_worker():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    while running:

        text = speech_queue.get()

        if text is None:
            break

        try:
            audio_state.start_speaking(hold_seconds=1.8)

            print(f"[JARVIS ASYNC TTS]: {text}")

            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as f:
                path = f.name

            loop.run_until_complete(_generate_audio(text, path))

            # play audio (blocking but inside worker only)
            pygame.mixer.music.load(path)
            pygame.mixer.music.play()

            while pygame.mixer.music.get_busy():
                continue

            os.remove(path)

            print("[TTS DONE]")

        except Exception as e:
            print(f"[TTS ERROR] {e}")

        finally:
            audio_state.stop_speaking()
            speech_queue.task_done()


# =========================
# PUBLIC API
# =========================
def start_tts_engine():
    thread = threading.Thread(target=_tts_worker, daemon=True)
    thread.start()


def speak(text: str):
    if not text:
        return
    speech_queue.put(text)


def stop_tts():
    global running
    running = False
    speech_queue.put(None)