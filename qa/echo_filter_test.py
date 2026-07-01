"""qa/echo_filter_test.py — verify the self-echo filter discriminates correctly."""
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from core.alive_kernel import _is_self_echo, _remember_spoken
import core.alive_kernel as ak

ak._ECHO_HISTORY.clear()
_remember_spoken("The current time is 10:30 PM.")
print("short (time):", _is_self_echo("time"))           # False (under min_tokens)
print("short (now):", _is_self_echo("now"))             # False
print("exact echo:", _is_self_echo("the current time is 10:30 pm"))  # True
print("real echo (hours 57 minutes):", _is_self_echo("hours 57 minutes"))  # False (low overlap)
print("legit follow-up:", _is_self_echo("jarvis what is the date"))  # False

ak._ECHO_HISTORY.clear()
_remember_spoken("May holidays: Memorial Day.")
print("medium echo (memorial day):", _is_self_echo("memorial day is in may"))  # True
