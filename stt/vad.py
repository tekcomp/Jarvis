import webrtcvad
import collections
import pyaudio
import numpy as np

# -----------------------------
# VAD CONFIG
# -----------------------------
vad = webrtcvad.Vad(2)  # 0=least strict, 3=most strict

RATE = 16000
FRAME_MS = 30
FRAME_SIZE = int(RATE * FRAME_MS / 1000)

MAX_SILENCE_FRAMES = 25   # ~750ms pause = end of speech (CRITICAL)

# -----------------------------
# AUDIO STREAM
# -----------------------------
audio = pyaudio.PyAudio()

stream = audio.open(
    format=pyaudio.paInt16,
    channels=1,
    rate=RATE,
    input=True,
    frames_per_buffer=FRAME_SIZE
)

# -----------------------------
# MAIN GENERATOR
# -----------------------------
def get_speech_frames():
    """
    Yields complete utterances as numpy int16 arrays.
    This is the core "sentence segmentation" layer.
    """

    voiced_frames = []
    triggered = False
    silence_count = 0

    while True:
        frame = stream.read(FRAME_SIZE, exception_on_overflow=False)

        # WebRTC VAD expects raw bytes (16-bit mono PCM)
        is_speech = vad.is_speech(frame, RATE)

        # -----------------------------
        # SPEECH DETECTED
        # -----------------------------
        if is_speech:
            voiced_frames.append(frame)
            triggered = True
            silence_count = 0

        # -----------------------------
        # SILENCE AFTER SPEECH
        # -----------------------------
        elif triggered:
            silence_count += 1

            # Still within pause threshold → keep buffering
            if silence_count < MAX_SILENCE_FRAMES:
                continue

            # -----------------------------
            # END OF SPEECH DETECTED
            # -----------------------------
            if voiced_frames:
                audio_bytes = b"".join(voiced_frames)

                yield np.frombuffer(audio_bytes, dtype=np.int16)

            # RESET STATE
            voiced_frames = []
            triggered = False
            silence_count = 0