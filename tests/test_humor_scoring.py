"""Session-aware humor scoring tests.

Run: python tests/test_humor_scoring.py
"""
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core import brain
from core.personality_engine_v2 import get_engine


def _ctx(mode="jarvis", mood="positive", bank="all"):
    eng = get_engine()
    eng.state.mode = mode
    eng.state.mood = mood
    return {"mode": mode, "mood": mood, "bank": bank,
            "hour": "morning", "dow": "mon", "recent_topics": set()}


def test_bank_affinity_changes_pick():
    """Jokes tagged with the current bank should outscore untagged strings
    when there's a single highest-scoring candidate, and the bank signal
    alone is enough to flip the winner from a plain-string pick."""
    brain._RECENT_JOKES.clear()
    brain._LAST_USED.clear()
    # With bank="jarvis" and hour/dow/mood that don't favor anything else,
    # the seeded jarvis joke (+1.0 bank) should outscore all plain strings (0).
    eng = get_engine()
    eng.state.mode = "jarvis"
    eng.state.mood = "neutral"
    ctx_match = {"bank": "jarvis", "mode": "jarvis", "mood": "neutral",
                 "hour": "evening", "dow": "wed", "recent_topics": set()}
    pick = brain._pick_joke(brain._JARVIS_JOKES, ctx_match)
    # The seeded jarvis joke should win.
    assert "optimize the reward function" in pick, f"expected bank-tagged joke, got {pick!r}"
    print(f"  [PASS] bank affinity picks tagged joke: {pick[:50]!r}")


def test_recent_joke_excluded():
    brain._RECENT_JOKES.clear()
    brain._LAST_USED.clear()
    pool = brain._ALL_JOKES
    first = brain._pick_joke(pool, _ctx())
    second = brain._pick_joke(pool, _ctx())
    assert first != second, f"anti-repeat failed: {first!r} == {second!r}"
    print(f"  [PASS] consecutive picks differ (anti-repeat): {first[:30]!r} != {second[:30]!r}")


def test_different_mode_different_pool():
    brain._RECENT_JOKES.clear()
    brain._LAST_USED.clear()
    eng = get_engine()
    eng.state.mode = "jarvis"
    a = brain._pick_joke(brain._ALL_JOKES, _ctx(mode="jarvis", bank="jarvis"))
    eng.state.mode = "playful"
    b = brain._pick_joke(brain._PLAYFUL_JOKES, _ctx(mode="playful", bank="playful"))
    assert a and b, "both picks should return non-empty strings"
    print(f"  [PASS] both pools produce jokes: all={a[:30]!r}  playful={b[:30]!r}")


def test_empty_pool_falls_back():
    brain._RECENT_JOKES.clear()
    brain._LAST_USED.clear()
    got = brain._pick_joke([], _ctx())
    assert got == "I've got nothing. Try again.", f"empty pool should fall back, got {got!r}"
    print(f"  [PASS] empty pool falls back: {got!r}")


def test_score_joke_string_vs_dict():
    brain._RECENT_JOKES.clear()
    brain._LAST_USED.clear()
    s1 = brain._score_joke("just a string", _ctx(mode="jarvis", bank="jarvis"))
    s2 = brain._score_joke({"text": "with meta", "bank": "jarvis", "topics": []}, _ctx(mode="jarvis", bank="jarvis"))
    assert isinstance(s1, float) and isinstance(s2, float)
    assert s2 > s1, f"dict with matching bank should outscore plain string: {s1} vs {s2}"
    print(f"  [PASS] dict metadata boosts score: str={s1:.3f}  dict={s2:.3f}")


def test_seeded_joke_picked_for_matching_context():
    """The seeded jarvis joke has time_fit=[morning, lunch] and tone=[nerdy,dry].
    In the morning with a 'dry' mood and bank=jarvis, it should outscore the 4 plain-string jokes."""
    brain._RECENT_JOKES.clear()
    brain._LAST_USED.clear()
    eng = get_engine()
    eng.state.mode = "jarvis"
    eng.state.mood = "dry"
    ctx = {"bank": "jarvis", "mode": "jarvis", "mood": "dry",
           "hour": "morning", "dow": "mon", "recent_topics": set()}
    pick = brain._pick_joke(brain._JARVIS_JOKES, ctx)
    assert "optimize the reward function" in pick, f"expected seeded joke, got {pick!r}"
    print(f"  [PASS] seeded joke wins on matching context: {pick[:50]!r}")


if __name__ == "__main__":
    fns = [v for k, v in list(globals().items()) if k.startswith("test_") and callable(v)]
    p = f = 0
    for fn in fns:
        try:
            fn()
            p += 1
        except Exception as e:
            print(f"  [FAIL] {fn.__name__}: {e}")
            f += 1
    print(f"humor: {p} passed / {f} failed")
    sys.exit(0 if f == 0 else 1)
