import numpy as np
import pyaudio

from core.logger import L3

from core.shutdown import is_shutdown

try:
    from core.audio_state import audio_state
except ImportError:
    from core.audio_state import AudioState
    audio_state = AudioState()

RATE = 16000
FRAME_SIZE = 1024

MIN_RMS = 80
MAX_SILENCE = 10
MIN_SPEECH = 6

MIN_AVG_ENERGY = 35


# =========================================================
# SAFE RMS
# =========================================================
def safe_rms(audio):

    if audio is None or len(audio) == 0:
        return 0.0

    audio = audio.astype(np.float32)

    val = np.mean(audio ** 2)

    if np.isnan(val) or val <= 0:
        return 0.0

    return float(np.sqrt(val))


# =========================================================
# AUDIO QUALITY FILTER
# =========================================================
def is_valid_audio(buffer):

    if len(buffer) < MIN_SPEECH:
        return False

    total_energy = 0.0

    for chunk in buffer:
        total_energy += np.mean(chunk.astype(np.float32) ** 2)

    avg_energy = total_energy / len(buffer)

    if avg_energy < MIN_AVG_ENERGY * 1.5:
        return False

    if len(buffer) < 8:
        return False

    return True


# =========================================================
# MAIN VAD GENERATOR
# =========================================================
def get_speech_frames():

    pa = pyaudio.PyAudio()

    device_index = pa.get_default_input_device_info()["index"]

    stream = pa.open(
        format=pyaudio.paInt16,
        channels=1,
        rate=RATE,
        input=True,
        input_device_index=device_index,
        frames_per_buffer=FRAME_SIZE,
    )

    print("[VAD] ENGINE STABLE MODE")
    L3("VAD STABLE ONLINE")

    buffer = []
    silence = 0
    speech = 0
    triggered = False

    try:

        while not is_shutdown():

            try:

                frame = stream.read(
                    FRAME_SIZE,
                    exception_on_overflow=False,
                )

            except Exception as e:

                print(f"[VAD READ ERROR] {e}")
                continue

            audio = np.frombuffer(
                frame,
                dtype=np.int16,
            )

            # -------------------------------------------------
            # ECHO SUPPRESSION
            # -------------------------------------------------
            if not audio_state.mic_allowed():
                audio = np.zeros_like(audio)

            rms = safe_rms(audio)

            is_speech = rms > MIN_RMS

            # -------------------------------------------------
            # SPEECH
            # -------------------------------------------------
            if is_speech:

                buffer.append(audio)

                speech += 1
                silence = 0

                if not triggered and speech >= MIN_SPEECH:

                    triggered = True

                    L3("SPEECH START")

            # -------------------------------------------------
            # SILENCE
            # -------------------------------------------------
            else:

                if triggered:

                    silence += 1

                    buffer.append(audio)

                    if silence >= max(4, MAX_SILENCE // 2):

                        if is_valid_audio(buffer) and len(buffer) >= 12:

                            final_audio = np.concatenate(buffer)

                            final_audio = (
                                np.nan_to_num(final_audio)
                                .astype(np.int16)
                            )

                            L3(
                                f"SPEECH END frames={len(buffer)}"
                            )

                            print("[VAD] YIELD AUDIO")

                            yield final_audio

                        buffer = []
                        silence = 0
                        speech = 0
                        triggered = False

                else:

                    buffer = []
                    speech = 0

    finally:

        try:
            stream.stop_stream()
        except:
            pass

        try:
            stream.close()
        except:
            pass

        try:
            pa.terminate()
        except:
            pass

        print("[VAD] CLEAN EXIT COMPLETE")