import os

os.environ["CUDA_VISIBLE_DEVICES"] = ""

from kokoro import KPipeline
import soundfile as sf

pipeline = KPipeline(lang_code="a")

text = "Hello. My name is Jarvis. Voice synthesis is now operational."

generator = pipeline(
    text,
    voice="am_michael"
)

for i, (gs, ps, audio) in enumerate(generator):

    filename = f"jarvis_{i}.wav"

    sf.write(
        filename,
        audio,
        24000
    )

    print("Saved:", filename)