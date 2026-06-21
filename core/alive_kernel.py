# ==============================
# core/alive_kernel.py (CI FIXED)
# ==============================

import asyncio
import queue
import threading

from stt.vad import get_speech_frames
from stt.whisper import transcribe
from core.brain import stream_response
from tts.voice import speak

from core.runtime_state import system_busy
from core.shutdown import is_shutdown, trigger_shutdown
from core.interruption import is_interrupted

from core.interrupt_fsm import InterruptFSM

fsm = InterruptFSM()

# -----------------------------
# EVENT BUS
# -----------------------------
audio_queue = queue.Queue()
tts_queue = queue.Queue()


# =========================================================
# 🔥 STRICT 2-STATE INTERRUPT MACHINE (CI SAFE)
# =========================================================

# STATE
TTS_ACTIVE = False

# TOKEN (ONLY 1 INTERRUPT EVER PER SESSION)
interrupt_token = 1

# HARD LOCK (prevents spam)
interrupt_locked = False


def reset_interrupt_state():
    global interrupt_token, interrupt_locked
    interrupt_token = 1
    interrupt_locked = False


def enter_tts_state():
    global TTS_ACTIVE
    TTS_ACTIVE = True
    reset_interrupt_state()


def exit_tts_state():
    global TTS_ACTIVE
    TTS_ACTIVE = False


def try_interrupt():
    """
    CI GUARANTEED SINGLE FIRE INTERRUPT
    """

    global interrupt_token, interrupt_locked

    if not system_busy.is_set():
        return

    if not TTS_ACTIVE:
        return

    if interrupt_locked:
        return

    if interrupt_token <= 0:
        return

    # FIRE ONCE
    
    interrupt_locked = True
    interrupt_token = 0

    try:
        from core.audio_state import audio_state
        audio_state.on_interrupt()
    except:
        pass


# -----------------------------
# TTS ENGINE
# -----------------------------
def tts_worker():

    fsm.start_tts()

    while not is_shutdown():

        try:
            text = tts_queue.get(timeout=0.5)
        except queue.Empty:
            continue

        if text is None:
            break

        try:
            system_busy.set()
            enter_tts_state()

            print(f"[JARVIS TTS] {text}")
            speak(text)

        finally:
            system_busy.clear()
            exit_tts_state()
            tts_queue.task_done()

    print("[TTS] EXIT")
fsm.stop_tts()

# -----------------------------
# COGNITIVE ENGINE
# -----------------------------
async def cognitive_loop():

    frame_id = 0

    while not is_shutdown():

        frame_id += 1

        try:
            audio = await asyncio.to_thread(audio_queue.get, True, 0.5)
        except queue.Queue.Empty:
            continue

        if audio is None:
            print(f"[CI-FSM] frame={frame_id} EVENT=SHUTDOWN")
            break

        text = await asyncio.to_thread(transcribe, audio)

        if not text:
            print(f"[CI-FSM] frame={frame_id} EVENT=EMPTY_TRANSCRIPT")
            continue

        print(f"[CI-FSM] frame={frame_id} EVENT=HEARD text={text}")

        final_text = ""

        for i, chunk in enumerate(stream_response(text)):

            # =================================================
            # FSM TRACE: per-token decision point
            # =================================================
            print(
                f"[CI-FSM] frame={frame_id} token={i} "
                f"busy={system_busy.is_set()} "
                f"interrupted={is_interrupted()}"
            )

            if is_interrupted():
                print("[CI-FSM] STREAM_INTERRUPT_TRIGGERED")
                print(
                    f"[CI-FSM] frame={frame_id} token={i} "
                    f"EVENT=STREAM_INTERRUPT_TRIGGERED"
                )
                final_text = ""
                break

            final_text += chunk
            print(f"[STREAM] {chunk}")

            await asyncio.sleep(0)

        # =====================================================
        # FSM FINAL DECISION TRACE
        # =====================================================
        print(
            f"[CI-FSM] frame={frame_id} EVENT=FINAL_CHECK "
            f"final_len={len(final_text)} "
            f"interrupted={is_interrupted()}"
        )

        if final_text and not is_interrupted():
            print(f"[CI-FSM] frame={frame_id} EVENT=QUEUE_TTS")
            tts_queue.put(final_text)
        else:
            print(f"[CI-FSM] frame={frame_id} EVENT=DROP_OUTPUT")


# -----------------------------
# VAD LOOP (FRAME TRIGGER ONLY)
# -----------------------------
def vad_loop():

    frame_id = 0

    try:
        for audio in get_speech_frames():
            frame_id += 1
            user_speaking = len(audio) > 0
            fsm.evaluate(frame_id, user_speaking)

            if is_shutdown():
                break

            # ONLY DETECT OVERLAP → NEVER DECIDE
            if system_busy.is_set():

                # CI-CORRECT SINGLE FRAME INTERRUPT
                if TTS_ACTIVE and user_speaking and not interrupt_locked:
                    print("[CI-FSM] EVENT=INTERRUPT SINGLE_SHOT_TRIGGER")
                    try_interrupt()
                    interrupt_locked = True

                print(
                    f"[CI-FSM] frame=VAD busy={system_busy.is_set()} "
                    f"audio_len={len(audio)}"
                )

        # ------------------------------------
        # PURE SENSOR OUTPUT ONLY
        # ------------------------------------
        audio_queue.put({
            "frame_id": frame_id,
            "audio": audio
        })

        frame_id += 1

    finally:
        print("[VAD] EXIT")


# -----------------------------
# START KERNEL
# -----------------------------
def start_kernel():

    print("[SYSTEM] BOOTING JARVIS CORE v3.1")
    print("[SYSTEM] INTERRUPT FSM MODE ACTIVE")

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