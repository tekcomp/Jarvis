import asyncio
import queue
import threading
import time

from stt.vad import get_speech_frames
from stt.whisper import transcribe
from core.brain import stream_response
from tts.voice import speak

from core.audio_state import audio_state
from core.shutdown import is_shutdown, trigger_shutdown
from core.interruption import interrupt, is_interrupted


# =========================================================
# EVENT BUS
# =========================================================
audio_queue = queue.Queue()
tts_queue = queue.Queue()

system_busy = threading.Event()


# =========================================================
# TTS ENGINE (INTERRUPT SAFE)
# =========================================================
def tts_worker():

    while not is_shutdown():

        try:
            text = tts_queue.get(timeout=0.5)
        except queue.Empty:
            continue

        if text is None:
            break

        try:
            system_busy.set()

            audio_state.start_speaking(hold_seconds=1.2)

            print(f"[JARVIS TTS] {text}")

            speak(text)

        finally:
            audio_state.stop_speaking()
            system_busy.clear()
            tts_queue.task_done()

    print("[TTS] EXIT")


# =========================================================
# COGNITIVE ENGINE (STREAMING + INTERRUPTIBLE)
# =========================================================
async def cognitive_loop():

    while not is_shutdown():

        try:
            audio = await asyncio.to_thread(audio_queue.get, True, 0.5)
        except queue.Empty:
            continue

        if audio is None:
            break

        # ignore if speaking
        if system_busy.is_set():
            continue

        try:
            text = await asyncio.to_thread(transcribe, audio)

            if not text:
                continue

            print(f"[HEARD] {text}")

            # =================================================
            # STREAMING BRAIN (NEW v3.1)
            # =================================================
            response_stream = stream_response(text)

            final_text = ""

            for chunk in response_stream:

                # 🔥 INTERRUPT CHECK (CRITICAL)
                if is_interrupted():
                    print("[JARVIS] INTERRUPTED")
                    final_text = ""
                    break

                final_text += chunk
                print(f"[JARVIS STREAM] {chunk}")

                await asyncio.sleep(0)

            # =================================================
            # FINAL OUTPUT
            # =================================================
            if final_text and not is_interrupted():
                print(f"[JARVIS FINAL] {final_text}")
                tts_queue.put(final_text)

        except Exception as e:
            print(f"[PIPELINE ERROR] {e}")


    print("[COGNITIVE] LOOP EXIT")


# =========================================================
# VAD PRODUCER (INTERRUPT HOOK ADDED)
# =========================================================
def vad_loop():

    speech_active = False
    speech_lock_frames = 0
    interrupt_lock = False

    speech_session = False   # 🔥 NEW: global latch per utterance

    try:
        for audio in get_speech_frames():

            if is_shutdown():
                break

            # =================================================
            # INTERRUPT (SAFE SINGLE FIRE)
            # =================================================
            if system_busy.is_set() and not interrupt_lock:
                interrupt()
                audio_state.on_interrupt()
                interrupt_lock = True

            elif not system_busy.is_set():
                interrupt_lock = False

            # =================================================
            # ENERGY DETECTION
            # =================================================
            energy = len(audio)

            if energy > 0:

                speech_lock_frames += 1

                # =================================================
                # SPEECH START (ONLY ONCE PER SESSION)
                # =================================================
                if not speech_active and speech_lock_frames > 3:

                    speech_active = True

                    if not speech_session:
                        speech_session = True
                        print("[VAD] SPEECH START")

            else:

                if speech_active:
                    speech_active = False
                    speech_lock_frames = 0

                    print("[VAD] SPEECH END")

                    # =================================================
                    # RESET SESSION ONLY AFTER FULL END
                    # =================================================
                    speech_session = False

            audio_queue.put(audio)

    finally:
        print("[VAD] EXIT")

# =========================================================
# KERNEL START
# =========================================================
def start_kernel():

    print("[SYSTEM] BOOTING JARVIS ALIVE CORE v3.1")
    print("[SYSTEM] STREAMING + INTERRUPT MODE ACTIVE\n")

    threading.Thread(target=vad_loop, daemon=True).start()
    threading.Thread(target=tts_worker, daemon=True).start()

    try:
        asyncio.run(cognitive_loop())

    except KeyboardInterrupt:
        trigger_shutdown("keyboard interrupt")

    finally:
        trigger_shutdown("kernel exit")

        try:
            audio_queue.put(None)
            tts_queue.put(None)
        except:
            pass

        print("[SYSTEM] KERNEL SHUTDOWN COMPLETE")