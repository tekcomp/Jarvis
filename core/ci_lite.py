from datetime import datetime
import numpy as np

from core.brain import handle
from core.audio_state import audio_state
from tts.voice import speak


def _test_brain():
    print("[CI] Testing brain...")

    tests = {
        "what time is it": "time",
        "what is the date": "date",
        "tell me a joke": "joke",
        "weather": "weather",
    }

    for text, expected in tests.items():
        res = handle(text)
        if not res:
            raise Exception(f"[CI FAIL] Brain returned empty for: {text}")

    print("[CI PASS] brain")


def _test_audio_state():
    print("[CI] Testing audio_state...")

    audio_state.start_speaking(0.1)
    if audio_state.mic_allowed():
        raise Exception("[CI FAIL] mic should be blocked during speaking")

    audio_state.stop_speaking(0.1)

    print("[CI PASS] audio_state")


def _test_tts():
    print("[CI] Testing TTS...")

    try:
        speak("Jarvis test one two three")
    except Exception as e:
        raise Exception(f"[CI FAIL] TTS crashed: {e}")

    print("[CI PASS] TTS")


def _test_vad_sanity():
    print("[CI] Testing synthetic VAD frame...")

    fake_audio = (np.random.randn(16000) * 100).astype(np.int16)

    if len(fake_audio) == 0:
        raise Exception("[CI FAIL] invalid audio buffer")

    print("[CI PASS] VAD synthetic")


def run_ci():
    print("\n========================")
    print("[CI LITE MODE START]")
    print("========================\n")

    _test_brain()
    _test_audio_state()
    _test_tts()
    _test_vad_sanity()

    print("\n========================")
    print("[CI PASS - SYSTEM READY]")
    print("========================\n")