"""Smoke test: feed 'System shutting down.' through the real TTS chain, then exit."""
import time, threading, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# Boot only what we need: TTS engine + speak path
from tts.voice_async import start_tts_engine, speak, stop_tts as tts_stop
from core.alive_kernel import tts_queue
from core.shutdown import trigger_shutdown

start_tts_engine()
time.sleep(0.4)

# Enqueue through the kernel queue (same path as shutdown handler)
tts_queue.put("System shutting down.")

# Wait for the speech_queue to drain by polling tts worker output.
# _tts_worker prints [TTS DONE] when finished; we approximate with a fixed wait.
time.sleep(6)

tts_queue.put(None)
trigger_shutdown("test-shutdown")
tts_stop()
time.sleep(0.4)
print("SHUTDOWN-ANNOUNCE TEST OK")
