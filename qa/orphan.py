"""Test orphan: load alive_kernel without booting, then sleep forever."""
import sys, os, time
sys.path.insert(0, r"C:\App\AI")
from core.alive_kernel import tts_worker  # noqa: F401  (forces import / lock-in)
print(f"ORPHAN_PID={os.getpid()}", flush=True)
time.sleep(99999)
