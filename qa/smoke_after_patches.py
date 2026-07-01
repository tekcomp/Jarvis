"""qa/smoke_after_patches.py — end-to-end smoke test of all four patches."""
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.wc_intent import handle_wc_intent as h
from core.alive_kernel import intent_router, _is_self_echo, _remember_spoken
from core.personality_engine_v2 import get_engine
import core.alive_kernel as ak

print("== intent_router ==")
for q in [
    "what is the time",
    "what is the date",
    "what holidays are in may",
    "when does usa play next",
    "world cup opener",
    "goodbye",
]:
    r = intent_router(q)
    print(f"  {q!r} -> {r!r}")

print()
print("== wc_intent (full data) ==")
for q in [
    "when does usa play next",
    "united states schedule",
    "world cup today",
    "what is the usa economy",  # must NOT trigger WC
]:
    print(f"  {q!r} -> {h(q)!r}")

print()
print("== echo filter ==")
ak._ECHO_HISTORY.clear()
_remember_spoken("The current time is 10:30 PM.")
print("  exact echo:", _is_self_echo("the current time is 10:30 pm"))
print("  short (time):", _is_self_echo("time"))
print("  legit follow-up:", _is_self_echo("jarvis what is the date"))

print()
print("== personality singleton ==")
e1 = get_engine()
e2 = get_engine()
print("  same instance:", e1 is e2)
