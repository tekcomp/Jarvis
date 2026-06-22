# ==============================
# core/alive_kernel.py (FINAL STABLE AUDIO FIX v4)
# ==============================

import asyncio
import queue
import threading
import time
import datetime

from stt.vad import get_speech_frames
from stt.whisper import transcribe
from core.brain import stream_response
from tts.voice import speak

from core.runtime_state import system_busy
from core.shutdown import is_shutdown, trigger_shutdown
from core.interruption import is_interrupted
from core.interrupt_fsm import InterruptFSM
from core.audio_state import audio_state

from core.personality_engine_v2 import get_engine
from core.response_guard import ResponseGuard


# =========================================================
# INIT
# =========================================================
fsm = InterruptFSM()
personality = get_engine()
response_guard = ResponseGuard()

audio_queue = queue.Queue()
tts_queue = queue.Queue()


# =========================================================
# INTENT ENGINE (HARD GUARANTEE LAYER)
# =========================================================
def intent_router(text: str):

    t = text.lower()
    now = datetime.datetime.now()

    if "time" in t:
        return f"The current time is {now.strftime('%H:%M:%S')}."

    if "date" in t:
        return f"Today is {now.strftime('%A, %B %d, %Y')}."

    if "joke" in t:
        return "Why did the AI cross the road? To optimize the reward function."

    return None


# =========================================================
# AUDIO CHECK
# =========================================================
def has_audio(audio):
    return audio is not None and len(audio) > 0


# =========================================================
# TTS WORKER
# =========================================================
def tts_worker():

    fsm.start_tts()

    try:
        while not is_shutdown():

            try:
                text = tts_queue.get(timeout=0.5)
            except queue.Empty:
                continue

            if text is None:
                break

            system_busy.set()
            audio_state.tts_started()

            try:
                print(f"[JARVIS TTS] {text}")
                speak(text)

            finally:
                system_busy.clear()
                audio_state.tts_finished()
                tts_queue.task_done()

    finally:
        print("[TTS] EXIT")
        fsm.stop_tts()


# =========================================================
# COGNITIVE LOOP (FIXED - NO SILENCE POSSIBLE)
# =========================================================
async def cognitive_loop():

    print("[CI-BOOT] cognitive_loop STARTED")

    frame_id = 0

    while not is_shutdown():

        try:
            packet = audio_queue.get(timeout=0.5)
        except queue.Empty:
            await asyncio.sleep(0.03)
            continue

        if packet is None:
            break

        audio = packet.get("audio")

        if not has_audio(audio):
            continue

        if not audio_state.mic_allowed():
            continue

        frame_id += 1

        text = transcribe(audio)

        if not text:
            continue

        text = text.strip().lower()

        print(f"[CI-AUDIO] HEARD: {text}")

        # =================================================
        # 🔥 CRITICAL FIX: UPDATE PERSONALITY HERE
        # =================================================
        personality.update(text)

        print(f"[CI-MODE] mode={personality.state.mode} mood={personality.state.mood}")

        # =================================================
        # LAYER 1 — INTENT
        # =================================================
        intent = intent_router(text)

        if intent:
            print(f"[CI-INTENT] {intent}")
            tts_queue.put(intent)
            continue

        # =================================================
        # LAYER 2 — LLM
        # =================================================
        final_text = ""

        try:
            for chunk in stream_response(
                text,
                system_prompt=personality.system_prompt()
            ):

                if is_interrupted():
                    final_text = ""
                    break

                final_text += chunk

        except Exception as e:
            print(f"[CI-ERROR] stream_response failed: {e}")
            final_text = ""

        final_text = final_text.strip()

        # =================================================
        # LAYER 3 — FALLBACK
        # =================================================
        if not final_text:
            print("[CI-FALLBACK] triggered")

            # MODE-AWARE FALLBACK (THIS IS WHAT YOU WERE MISSING)
            mode = personality.state.mode

            if mode == "playful":
                final_text = "Haha 😄 I'm in playful mode now!"

            elif mode == "jarvis":
                final_text = "Understood. Jarvis mode active."

            else:
                final_text = "I understand. How can I help you?"

        print(f"[CI-TTS] {final_text}")

        response_guard.update(text, final_text)
        tts_queue.put(final_text)

# =========================================================
# VAD LOOP
# =========================================================
def vad_loop():

    frame_id = 0

    try:
        for audio in get_speech_frames():

            if is_shutdown():
                break

            if not has_audio(audio):
                continue

            if not audio_state.mic_allowed():
                continue

            frame_id += 1

            fsm.evaluate(frame_id, True)

            audio_queue.put({
                "frame_id": frame_id,
                "audio": audio
            })

            print("[CI-VAD] PUSH")

    finally:
        print("[VAD] EXIT")


# =========================================================
# START KERNEL
# =========================================================
def start_kernel():

    print("[SYSTEM] AGENT v3 BOOT")
    print("[SYSTEM] AUDIO GATE ENABLED")

    threading.Thread(target=vad_loop, daemon=True).start()
    threading.Thread(target=tts_worker, daemon=True).start()

    try:
        asyncio.run(cognitive_loop())

    except KeyboardInterrupt:
        trigger_shutdown("keyboard")

    finally:
        trigger_shutdown("exit")

        audio_queue.put(None)
        tts_queue.put(None)

        fsm.stop_tts()

        print("[SYSTEM] SHUTDOWN COMPLETE")