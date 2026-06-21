from audio.aec import should_block_audio
from audio.speaker_gate import is_authorized_speaker


def process(audio):

    if audio is None:
        return None

    if should_block_audio():
        print("[AUDIO] blocked by echo guard")
        return None

    if not is_authorized_speaker(audio):
        print("[AUDIO] speaker rejected")
        return None

    return audio