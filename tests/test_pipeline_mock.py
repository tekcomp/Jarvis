import time
from core.contract import handle


MOCK_AUDIO_INPUTS = [
    "jarvis what time is it",
    "tell me a joke",
    "what is the date",
    "jarvis tell me a joke again",
]


def fake_transcribe(audio_chunk: str):
    return audio_chunk


def fake_speak(text: str):
    print(f"[MOCK TTS] {text}")
    time.sleep(0.05)  # simulate speech delay


def run_pipeline_tests():

    print("\n[CI] PIPELINE MOCK TESTS")

    passed = 0
    failed = 0

    for audio in MOCK_AUDIO_INPUTS:

        text = fake_transcribe(audio)
        response = handle(text)

        if response:
            fake_speak(response)
            passed += 1
        else:
            failed += 1

    print(f"Pipeline: {passed} passed / {failed} failed")

    return {"passed": passed, "failed": failed}