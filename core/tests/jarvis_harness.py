"""
Jarvis Test Harness v1
- lightweight regression + smoke test runner
- no pytest dependency
- runs core pipeline checks in isolation
"""

import time

from stt.whisper import transcribe
from core.brain import handle
from tts.voice import speak
from stt.vad import get_speech_frames


# =========================================================
# TEST 1: BRAIN INTENT TESTS
# =========================================================
def test_brain():
    print("\n[TEST] Brain Intent Tests")

    cases = {
        "what time is it": "time",
        "what is today's date": "date",
        "tell me a joke": "joke",
    }

    for input_text, expected in cases.items():
        result = handle(input_text)
        print(f"[BRAIN] {input_text} -> {result}")

        assert result is not None, "Brain returned None"
        assert expected in result.lower(), f"Expected '{expected}' in response"

    print("[TEST] Brain OK")


# =========================================================
# TEST 2: TTS SMOKE TEST
# =========================================================
def test_tts():
    print("\n[TEST] TTS Smoke Test")

    speak("Jarvis test one")
    time.sleep(0.5)

    speak("Jarvis test two")
    time.sleep(1)

    print("[TEST] TTS OK (check speakers manually)")


# =========================================================
# TEST 3: WHISPER + VAD PIPELINE
# =========================================================
def test_vad_whisper():
    print("\n[TEST] VAD + Whisper Pipeline")

    print("Speak NOW (2-3 seconds test input)...")

    audio = next(get_speech_frames())

    text = transcribe(audio)

    print(f"[WHISPER] {text}")

    assert text is not None
    assert len(text.strip()) > 0

    print("[TEST] VAD + Whisper OK")


# =========================================================
# TEST 4: FULL PIPELINE LOOP
# =========================================================
def test_full_loop():
    print("\n[TEST] FULL PIPELINE (1 cycle)")

    audio = next(get_speech_frames())
    text = transcribe(audio)

    print(f"[PIPELINE] HEARD: {text}")

    response = handle(text)

    print(f"[PIPELINE] RESPONSE: {response}")

    if response:
        speak(response)

    assert response is not None

    print("[TEST] FULL PIPELINE OK")


# =========================================================
# RUNNER
# =========================================================
def run_all():
    print("\n==============================")
    print(" JARVIS TEST HARNESS v1")
    print("==============================")

    try:
        test_brain()
        test_tts()
        test_vad_whisper()
        test_full_loop()

        print("\nALL TESTS PASSED ✅")

    except AssertionError as e:
        print("\nTEST FAILED ❌")
        print(e)

    except Exception as e:
        print("\nCRASH ❌")
        print(e)


if __name__ == "__main__":
    run_all()