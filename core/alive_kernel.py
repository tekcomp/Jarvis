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
from tts.voice_async import speak, start_tts_engine

from core.runtime_state import system_busy
from core.shutdown import is_shutdown, trigger_shutdown
from core.interruption import is_interrupted
from core.interrupt_fsm import InterruptFSM
from core.audio_state import audio_state

from core.personality_engine_v2 import get_engine
from core.response_guard import ResponseGuard
from core.noise_filter import is_valid_transcript


from core.wake_gate import contains_wake_word, strip_wake_word
from core.session_manager import (
    open_session,
    touch,
    session_active,
)

# =========================================================
# INIT
# =========================================================
fsm = InterruptFSM()
personality = get_engine()
response_guard = ResponseGuard()

audio_queue = queue.Queue()
tts_queue = queue.Queue()


# =========================================================
# ECHO SELF-TEXT FILTER
# =========================================================
# Keeps the last few things Jarvis actually said. If Whisper transcribes
# something that overlaps heavily with a recent TTS line, we assume the mic
# picked up the bot's own audio and drop the utterance.
_ECHO_HISTORY = []   # list[str] — most recent TTS lines, max 3
_ECHO_HISTORY_MAX = 3


def _remember_spoken(text: str) -> None:
    if not text:
        return
    _ECHO_HISTORY.append(text.lower().strip())
    if len(_ECHO_HISTORY) > _ECHO_HISTORY_MAX:
        _ECHO_HISTORY.pop(0)


def _is_self_echo(text: str, threshold: float = 0.6, min_tokens: int = 3) -> bool:
    """True if `text` looks like an echo of the last TTS utterance.

    Uses token-overlap ratio against the most recent spoken line. Threshold
    0.6 means >=60% of the new tokens were in the previous utterance.
    `min_tokens` rejects very short inputs (1-2 words) so a one-word follow-up
    like 'time' after a time answer doesn't get classified as an echo.
    """
    if not _ECHO_HISTORY:
        return False
    heard = text.lower().split()
    if len(heard) < min_tokens:
        return False
    heard_set = set(heard)
    last = _ECHO_HISTORY[-1]
    spoken = set(last.split())
    if not spoken:
        return False
    overlap = len(heard_set & spoken) / max(len(heard_set), 1)
    return overlap >= threshold


# =========================================================
# TRANSCRIPT LOGGER
# =========================================================
# Append every STT-heard phrase and every TTS-spoken line to
# logs/transcript.log with ISO-8601 timestamps. Two roles: USER (what
# Whisper transcribed) and JARVIS (what TTS said). The file is plain
# text, one line per event, and safe to tail with `Get-Content -Wait`.
#
# This is the single best place to look for:
#   - "What did I just say?"  -> grep USER
#   - "What did Jarvis say?"  -> grep JARVIS
#   - "Did the user say X or Y?" -> compare timestamps in USER
#   - "When was the last conversation?" -> sort by timestamp
import os as _os_transcript

_TRANSCRIPT_PATH = _os_transcript.path.join(
    _os_transcript.path.dirname(_os_transcript.path.abspath(__file__)),
    "..", "logs", "transcript.log",
)
_TRANSCRIPT_LOCK = threading.Lock()


def _log_transcript(role: str, text: str, intent: str = "") -> None:
    """Append a single event to logs/transcript.log. Failures are silent.

    `intent` is an optional tag describing which layer fired
    (e.g. "joke", "time", "version", "llm"). When present it appears in
    square brackets so the log is easy to filter:

        2026-07-01T01:33:43 [joke] USER: jarvis tell me a joke
        2026-07-01T01:33:43 [joke] JARVIS: Why did the AI cross the road?...
    """
    if not text:
        return
    try:
        ts = datetime.datetime.now().isoformat(timespec="seconds")
        tag = f"[{intent}] " if intent else ""
        with _TRANSCRIPT_LOCK:
            with open(_TRANSCRIPT_PATH, "a", encoding="utf-8") as f:
                f.write(f"{ts} {tag}{role}: {text.strip()}\n")
    except Exception:
        # Transcript logging is best-effort; never crash the kernel.
        pass


# Coarse-grained tag for canned (Layer-1) intents. Used to label the
# JARVIS line in the transcript. Not perfect — there is overlap (e.g.
# "tell me a joke about march" matches both joke and holiday) — but the
# first match wins which is fine for a transcript summary.
def _classify_canned_intent(text: str) -> str:
    t = text.lower()
    if any(w in t for w in ("playful mode", "jarvis mode", "assistant mode")):
        return "mode"
    if "jarvis" in t and not any(w in t for w in ("joke", "time", "date", "holiday", "world cup")):
        return "mode"
    if "assistant" in t:
        return "mode"
    if "joke" in t:
        return "joke"
    if "time" in t:
        return "time"
    if "date" in t or "today" in t:
        return "date"
    if "bye" in t or "shutdown" in t or "goodbye" in t:
        return "shutdown"
    if any(m in t for m in (
        "january", "february", "march", "april", "may", "june", "july",
        "august", "september", "october", "november", "december",
    )):
        return "holiday"
    return "canned"


# =========================================================
# INTENT ENGINE (HARD GUARANTEE LAYER)
# =========================================================
def intent_router(text: str):

    t = text.lower().strip()
    now = datetime.datetime.now()

    # ---- Voice shutdown (no wake word required) ----
    SHUTDOWN_PHRASES = ("goodbye", "shut down", "shutdown", "power off", "go to sleep")
    if any(p == t or p in t for p in SHUTDOWN_PHRASES):
        return {"kind": "shutdown", "text": "Goodbye, sir."}

    if "time" in t:
        return f"The current time is {now.strftime('%I:%M %p')}."

    if "date" in t:
        return f"Today is {now.strftime('%A, %B %d, %Y')}."
    
    if "joke" in t:
        return "Why did the AI cross the road? To optimize the reward function."

    # ---------------------------------
    # HOLIDAYS
    # ---------------------------------

    if "holiday" in t:

        if "january" in t:
            return "January holidays: New Year's Day, Martin Luther King Jr. Day."

        if "february" in t:
            return "February holidays: Presidents Day, Valentine's Day."

        if "march" in t:
            return "March holidays: St. Patrick's Day."

        if "april" in t:
            return "April holidays: Easter, Earth Day."

        if "may" in t:
            return "May holidays: Memorial Day."

        if "june" in t:
            return "June holidays: Juneteenth, Father's Day."

        if "july" in t:
            return "July holidays: Independence Day."

        if "august" in t:
            return "August holidays: No major U.S. federal holidays."

        if "september" in t:
            return "September holidays: Labor Day."

        if "october" in t:
            return "October holidays: Columbus Day, Halloween."

        if "november" in t:
            return "November holidays: Veterans Day, Thanksgiving."

        if "december" in t:
            return "December holidays: Christmas Eve, Christmas Day, New Year's Eve."

        return "Please specify a month."

    # ---- World Cup 2026 voice intent ----
    try:
        from core.wc_intent import handle_wc_intent
        wc_answer = handle_wc_intent(t)
        if wc_answer:
            return wc_answer
    except Exception as e:
        print(f"[CI-WC] error: {e}")

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
                item = tts_queue.get(timeout=0.5)
            except queue.Empty:
                continue

            if item is None:
                break

            # Accept either legacy plain-string items or new (text, intent)
            # tuples so the worker stays compatible with anything that
            # still puts a bare string on the queue.
            if isinstance(item, tuple) and len(item) == 2:
                text, intent_tag = item
            else:
                text, intent_tag = item, ""

            system_busy.set()
            audio_state.tts_started()

            try:
                print(f"[JARVIS TTS] {text}")
                # Record what we're about to say so the echo filter can
                # suppress a Whisper transcript that bleeds back from speakers.
                _remember_spoken(text)
                _log_transcript("JARVIS", text, intent=intent_tag)
                print("BEFORE SPEAK")
                speak(text)
                print("AFTER SPEAK")
            except Exception as e:
                print("TTS ERROR:", e)
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

        if not is_valid_transcript(text):
            print(f"[CI-FILTER] rejected: {text}")
            continue

        if _is_self_echo(text):
            print(f"[CI-ECHO] self-echo dropped: {text}")
            continue

        print(f"[CI-AUDIO] HEARD: {text}")
        _log_transcript("USER", text)

        # =================================================
        # WAKE GATE V1
        # =================================================

        if contains_wake_word(text):

            open_session()

            text = strip_wake_word(text)

            if not text:
                tts_queue.put(("Yes sir.", "wake_only"))
                continue

        elif not session_active():

            print("[WAKE] ignored")
            continue

        else:
            touch()

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
            # Tagged shutdown intent (dict) bypasses text reply path
            if isinstance(intent, dict) and intent.get("kind") == "shutdown":
                print(f"[CI-INTENT] {intent}")
                tts_queue.put((intent["text"], "shutdown"))
                # Wait for the spoken line, then end the loop.
                try:
                    while not tts_queue.empty():
                        await asyncio.sleep(0.1)
                except Exception:
                    pass
                break  # exit cognitive_loop; finally{} handles graceful shutdown

            print(f"[CI-INTENT] {intent}")
            # Classify the canned intent for the transcript tag. This
            # is a coarse label; the LLM fallback below tags itself.
            canned_tag = _classify_canned_intent(text)
            tts_queue.put((intent, canned_tag))
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
                final_text = "How can I help you?"

        print(f"[CI-TTS] {final_text}")

        response_guard.update(text, final_text)
        tts_queue.put((final_text, "llm"))

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

    # ---- PID marker so Kill_Jarvis can stop us cleanly ----
    try:
        import os
        pid_path = os.path.join(os.path.dirname(__file__), "..", "state", "kernel.pid")
        os.makedirs(os.path.dirname(pid_path), exist_ok=True)
        with open(pid_path, "w") as f:
            f.write(str(os.getpid()))
        print(f"[SYSTEM] pid marker: {os.path.abspath(pid_path)}")
    except Exception as e:
        print(f"[SYSTEM] pid marker failed (non-fatal): {e}")

    threading.Thread(target=vad_loop, daemon=True).start()
    threading.Thread(target=tts_worker, daemon=True).start()
    start_tts_engine()

    # ---- Startup chime: confirms audio path is alive ----
    print("[SYSTEM] boot chime queued")
    tts_queue.put("System online.")

    # ---- Heartbeat logger: write a 1-line "still alive" ping every 30s
    # to logs/heartbeat.log so silence in the main log is distinguishable
    # from a dead process.
    import os as _hb_os
    _hb_path = _hb_os.path.join(_hb_os.path.dirname(__file__), "..", "logs", "heartbeat.log")
    try:
        _hb_os.makedirs(_hb_os.path.dirname(_hb_path), exist_ok=True)
        # Write a session-start banner so each run is visibly demarcated.
        try:
            with open(_hb_path, "a", encoding="utf-8") as _bf:
                _bf.write(
                    f"[{datetime.datetime.now().isoformat(timespec='seconds')}] "
                    f"=== SESSION START pid={_hb_os.getpid()} ===\n"
                )
        except Exception:
            pass
        def _heartbeat():
            _start = time.time()
            while not is_shutdown():
                try:
                    with open(_hb_path, "a", encoding="utf-8") as _f:
                        _f.write(
                            f"[{datetime.datetime.now().isoformat(timespec='seconds')}] "
                            f"alive uptime={int(time.time()-_start)}s "
                            f"mic_allowed={audio_state.mic_allowed()} "
                            f"session_active={session_active()}\n"
                        )
                except Exception:
                    pass
                time.sleep(30)
        threading.Thread(target=_heartbeat, daemon=True).start()
        print(f"[SYSTEM] heartbeat -> {_hb_os.path.abspath(_hb_path)}")
    except Exception as e:
        print(f"[SYSTEM] heartbeat start failed (non-fatal): {e}")

    # ---- Shutdown announcement (graceful) ----
    def _announce_and_quit(_signum=None, _frame=None):
        try:
            print("[SYSTEM] shutdown signal received, announcing...")
            tts_queue.put("System shutting down.")
            # let TTS worker pick it up
            tts_queue.join()
        except Exception as e:
            print(f"[SYSTEM] announce error: {e}")
        finally:
            trigger_shutdown("signal")
            try:
                import os
                # raise from main thread so asyncio.run returns
                os._exit(0)
            except Exception:
                pass

    # Wire SIGTERM (sent by Kill_Jarvis) and SIGINT (Ctrl+C)
    try:
        import signal as _signal
        _signal.signal(_signal.SIGTERM, _announce_and_quit)
        _signal.signal(_signal.SIGINT, _announce_and_quit)
    except Exception as e:
        # Windows may not expose SIGTERM to all Python builds; fall through to KeyboardInterrupt path
        print(f"[SYSTEM] signal handler install skipped: {e}")

    try:
        asyncio.run(cognitive_loop())

    except KeyboardInterrupt:
        # Ctrl+C path: announce then exit
        try:
            tts_queue.put("System shutting down.")
            tts_queue.join()
        except Exception:
            pass
        trigger_shutdown("keyboard")

    finally:
        trigger_shutdown("exit")

        audio_queue.put(None)
        try:
            tts_queue.put(None)
        except Exception:
            pass

        # remove pid marker
        try:
            import os
            pid_path = os.path.join(os.path.dirname(__file__), "..", "state", "kernel.pid")
            if os.path.exists(pid_path):
                os.remove(pid_path)
        except Exception:
            pass

        fsm.stop_tts()

        print("[SYSTEM] SHUTDOWN COMPLETE")