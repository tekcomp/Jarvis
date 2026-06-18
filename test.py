import os
os.environ["CUDA_VISIBLE_DEVICES"] = ""

from kokoro import KPipeline

pipeline = KPipeline(lang_code="a")
print("Pipeline created")
