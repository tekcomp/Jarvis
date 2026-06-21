# ==============================
# core/audio_frontend.py (PRODUCTION FRONTEND v1)
# ==============================

import time
import queue
import threading
import numpy as np

# OPTIONAL (WebRTC AEC)
try:
    import webrtc_audio_processing as webrtc
    AEC_AVAILABLE = True
except Exception:
    AEC_AVAILABLE = False


# =========================================================
# GLOBAL STATE
# =========================================================
class AudioFrontendState:
    def __init__(self):
        self.tts_active_until = 0
        self.last_tts_audio = None
        self.lock = threading.Lock()

state = AudioFrontendState()


# =========================================================
# TTS CONTEXT FEED (CRITICAL FOR AEC)
# =========================================================
def feed_tts_audio(audio_chunk):
    """
    Feed speaker output into echo canceller reference buffer.
    """
    with state.lock:
        state.last_tts_audio = audio_chunk


def mark_tts(duration_sec=2.5):
    """
    Soft echo suppression window (backup layer).
    """
    with state.lock:
        state.tts_active_until = time.time() + duration_sec


def is_echo_window():
    with state.lock:
        return time.time() < state.tts_active_until


# =========================================================
# AEC ENGINE
# =========================================================
class EchoCanceller:

    def __init__(self):
        self.enabled = AEC_AVAILABLE

        if self.enabled:
            self.aec = webrtc.AudioProcessing(
                enable_aec=True,
                enable_ns=True,
                enable_agc=True
            )

    def process(self, mic_audio):

        # fallback if no AEC installed
        if not self.enabled:
            return mic_audio

        try:
            ref = state.last_tts_audio

            if ref is None:
                return mic_audio

            return self.aec.process_stream(
                mic_audio,
                ref
            )

        except Exception:
            return mic_audio


aec_engine = EchoCanceller()


# =========================================================
# SPEAKER GUARD (LIGHTWEIGHT HEURISTIC LAYER)
# =========================================================
def is_self_audio(mic_audio):
    """
    Prevent TTS bleed re-entry.
    """

    if is_echo_window():
        return True

    if state.last_tts_audio is None:
        return False

    # simple energy similarity check
    try:
        mic_energy = np.mean(np.abs(mic_audio))
        tts_energy = np.mean(np.abs(state.last_tts_audio))

        if tts_energy == 0:
            return False

        ratio = mic_energy / (tts_energy + 1e-6)

        # if too similar → likely echo
        if 0.7 < ratio < 1.3:
            return True

    except Exception:
        pass

    return False


# =========================================================
# FRONT-END PROCESSOR PIPELINE
# =========================================================
def process_audio_stream(raw_audio_iter, output_queue, fsm, system_busy, vad_fn):
    """
    Main production pipeline.
    """

    frame_id = 0

    for audio in raw_audio_iter:

        frame_id += 1

        # -----------------------------
        # 1. HARD BLOCK SYSTEM AUDIO
        # -----------------------------
        if is_self_audio(audio):
            continue

        # -----------------------------
        # 2. AEC CLEANING
        # -----------------------------
        clean_audio = aec_engine.process(audio)

        # -----------------------------
        # 3. VAD FILTER
        # -----------------------------
        try:
            speech = vad_fn(clean_audio)
        except Exception:
            speech = len(clean_audio) > 0

        fsm.evaluate(frame_id, speech)

        if not speech:
            continue

        # -----------------------------
        # 4. SYSTEM BUSY CHECK
        # -----------------------------
        if system_busy.is_set():
            continue

        # -----------------------------
        # 5. PUSH CLEAN PACKET
        # -----------------------------
        output_queue.put({
            "frame_id": frame_id,
            "audio": clean_audio
        })

        print(f"[AUDIO-FE] FRAME {frame_id} PUSHED")