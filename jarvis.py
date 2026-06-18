import numpy as np
import sounddevice as sd
import queue
from state import state

from llm import stream_llm
from jarvis_voice import speak
from wake import detect_wake
from stt_stream import transcribe_audio_buffer

# -------------------------
# AUDIO STREAM
# -------------------------
q = queue.Queue()

def callback(indata, frames, time, status):
    q.put(indata.copy())

stream = sd.InputStream(
    samplerate=16000,
    channels=1,
    dtype="float32",
    callback=callback
)
stream.start()

buffer = []
silence = 0

print("Jarvis ONLINE (Voice Mode)")

# -------------------------
# MAIN LOOP
# -------------------------
while True:
    audio = q.get().flatten()
    volume = np.abs(audio).mean()

    # speech detection
    if volume > 0.01:
        buffer.append(audio)
        silence = 0
    else:
        silence += 1

    # end of utterance
    if silence > 20 and len(buffer) > 15:

        print("Processing speech...")

        text = transcribe_audio_buffer(buffer) or ""

        text = text.strip()

        if len(text) == 0:
            buffer = []
            continue
    
        buffer = []

        print("Heard:", text)

        # -------------------------
        # WAKE WORD MODE
        # -------------------------
        if detect_wake(text):
            state.wake_word_detected = True
            speak("Yes?")
            continue

        # -------------------------
        # STOP COMMAND (BARGE IN)
        # -------------------------
        if "stop" in text:
            state.stop_speaking = True
            continue

        # -------------------------
        # AI RESPONSE (STREAMING)
        # -------------------------
        if state.wake_word_detected:
            state.wake_word_detected = False

            reply = ""

            for token in stream_llm(text):
                reply += token

            speak(reply)