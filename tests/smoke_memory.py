"""Smoke test for the new memory intent."""
import os
import sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from core import brain
from core.personality_engine_v2 import get_engine

# Reset state
engine = get_engine()
engine.mode = "jarvis"
brain.reset_memory()

print("--- Empty memory (no conversation yet) ---")
for q in ["jarvis what do you remember", "jarvis memory", "jarvis what's in your memory"]:
    out = brain.route_intent(q) or "(None)"
    print(f"  Q: {q!r:42s} -> {out}")

# Now simulate a conversation
print("\n--- After 2 turns ---")
_ = "".join(brain.stream_response("jarvis my favorite color is teal"))
_ = "".join(brain.stream_response("jarvis what time is it"))

for q in ["jarvis memory", "jarvis what do you remember", "jarvis what did I say"]:
    out = brain.route_intent(q) or "(None)"
    print(f"  Q: {q!r:42s} -> {out[:120]}{\"...\" if len(out) > 120 else \"\"}")
