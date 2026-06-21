# ==============================
# core/alive_kernel.py (CI FIXED v8 - NUMPY SAFE + STABLE PIPELINE)
# ==============================

import asyncio
from pydoc import text
import queue
import threading
import numpy as np

from stt.vad import get_speech_frames
from stt.whisper import transcribe
from core.brain import stream_response
from tts.voice import speak

from core.runtime_state import system_busy
from core.shutdown import is_shutdown, trigger_shutdown
from core.interruption import is_interrupted
from core.interrupt_fsm import InterruptFSM
from core.audio_frontend import process_audio_stream
from core.audio_frontend import feed_tts_audio, mark_tts

# =========================================================
# GLOBAL STATE
# =========================================================
fsm = InterruptFSM()

audio_queue = queue.Queue()
tts_queue = queue.Queue()

TTS_ACTIVE = False


# =========================================================
# AUDIO SAFETY CORE (FIXED NUMPY ISSUE)
# =========================================================
def has_audio(audio):

    if audio is None:
        return False

    # numpy array safe check
    if isinstance(audio, np.ndarray):
        return audio.size > 0

    # list / tuple safe check
    if isinstance(audio, (list, tuple)):
        return len(audio) > 0

    # bytes safe check
    if isinstance(audio, (bytes, bytearray)):
        return len(audio) > 0

    # fallback safe check
    try:
        return len(audio) > 0
    except Exception:
        return False


def is_self_audio_blocked():
    return system_busy.is_set()


# =========================================================
# TTS ENGINE
# =========================================================
def tts_worker():

    try:
        while not is_shutdown():

            try:
                text = tts_queue.get(timeout=0.5)
            except queue.Empty:
                continue

            if text is None:
                break

            system_busy.set()

            try:
                print(f"[JARVIS TTS] {text}")
                
                feed_tts_audio(text.encode() if isinstance(text, str) else text)
                mark_tts(len(text) * 0.08)

                speak(text)

            finally:
                system_busy.clear()
                tts_queue.task_done()

    finally:
        print("[TTS] EXIT")


# =========================================================
# COGNITIVE ENGINE (SAFE AUDIO HANDLING)
# =========================================================
async def cognitive_loop():

    print("[CI-BOOT] cognitive_loop STARTED")

    frame_id = 0

    while not is_shutdown():

        print("[CI-DEBUG] waiting for audio...")

        try:
            packet = audio_queue.get(timeout=0.5)
        except queue.Empty:
            await asyncio.sleep(0.05)
            continue

        if packet is None:
            break

        audio = packet.get("audio", None)

        # FIXED SAFE GUARD
        if not has_audio(audio):
            continue

        if is_self_audio_blocked():
            continue

        frame_id += 1

        print(f"[CI-AUDIO] RECEIVED frame={packet.get('frame_id')}")

        text = transcribe(audio)

        if not text:
            continue

        print(f"[CI-FSM] HEARD text={text}")

        # =============================
        # INTENT HANDLING (INLINE)
        # =============================
        t = text.lower()

        if "time" in t:
            from datetime import datetime
            reply = f"The time is {datetime.now().strftime('%H:%M:%S')}."
            tts_queue.put(reply)
            continue

        if "date" in t or "today" in t:
            from datetime import datetime
            reply = f"Today is {datetime.now().strftime('%A, %B %d, %Y')}."
            tts_queue.put(reply)
            continue

        if "joke" in t:
            tts_queue.put("Why did the AI cross the road? To optimize the reward function.")
            continue

        # =============================
        # LLM STREAM FALLBACK
        # =============================
        final_text = ""

        for chunk in stream_response(text):

            if is_interrupted():
                final_text = ""
                break

            final_text += chunk

        if final_text:
            tts_queue.put(final_text)


# =========================================================
# VAD LOOP
# =========================================================
def vad_loop():

    from stt.vad import get_speech_frames

    def vad_fn(audio):
        return len(audio) > 0  # replace with real VAD later

    process_audio_stream(
        raw_audio_iter=get_speech_frames(),
        output_queue=audio_queue,
        fsm=fsm,
        system_busy=system_busy,
        vad_fn=vad_fn
    )

# =========================================================
# START KERNEL
# =========================================================
def start_kernel():

    print("[SYSTEM] BOOTING JARVIS CORE v8 STABLE (NUMPY SAFE)")
    print("[SYSTEM] AUDIO TYPE SAFETY ENABLED")

    threading.Thread(target=vad_loop, daemon=True).start()
    threading.Thread(target=tts_worker, daemon=True).start()

    try:
        asyncio.run(cognitive_loop())

    except KeyboardInterrupt:
        trigger_shutdown("keyboard interrupt")

    finally:
        trigger_shutdown("kernel exit")

        audio_queue.put(None)
        tts_queue.put(None)

        print("[SYSTEM] SHUTDOWN COMPLETE")