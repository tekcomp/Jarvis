from core.personality_engine_v2 import get_engine
from core.holiday_engine import get_holidays

import os
import re
import json
import requests

engine = get_engine()

# =========================================================
# CONVERSATION MEMORY
# =========================================================
# Small ring buffer of recent user/assistant turns. Thread-safe enough for
# Jarvis's single-writer cognitive loop. Lets the LLM see the last few
# exchanges so it can answer "what did I just say?" honestly instead of
# inventing context.
import threading as _threading

_MEM_MAX = int(os.environ.get("JARVIS_MEM_TURNS", "6"))  # 6 = 3 user + 3 assistant
_MEMORY: list[dict] = []  # each entry: {"role": "user"|"assistant", "content": "..."}
_MEM_LOCK = _threading.Lock()


def _mem_push(role: str, content: str) -> None:
    if not content:
        return
    with _MEM_LOCK:
        _MEMORY.append({"role": role, "content": content.strip()})
        # keep only the last _MEM_MAX entries
        if len(_MEMORY) > _MEM_MAX:
            del _MEMORY[: len(_MEMORY) - _MEM_MAX]


def _mem_render() -> str:
    """Render recent turns as a plain-text transcript for the LLM prompt."""
    with _MEM_LOCK:
        if not _MEMORY:
            return ""
        lines = []
        for turn in _MEMORY:
            tag = "User" if turn["role"] == "user" else "Jarvis"
            lines.append(f"{tag}: {turn['content']}")
        return "\n".join(lines)


def reset_memory() -> None:
    """Wipe conversation memory (used on session reset / shutdown)."""
    with _MEM_LOCK:
        _MEMORY.clear()


# =========================================================
# LLM BACKEND (real Ollama call)
# =========================================================
# The kernel passes personality.system_prompt() in via the `system_prompt`
# argument. We hit the same Ollama endpoint the boot script verified, stream
# tokens, and yield them as they arrive so TTS can speak progressively.
_OLLAMA_URL = os.environ.get("JARVIS_OLLAMA_URL", "http://127.0.0.1:11434")
_OLLAMA_MODEL = os.environ.get("JARVIS_OLLAMA_MODEL", "gemma3:latest")
_OLLAMA_TIMEOUT = float(os.environ.get("JARVIS_OLLAMA_TIMEOUT", "30"))


def _llm_stream(prompt: str, system_prompt: str | None, transcript: str = ""):
    """Yield tokens from Ollama's /api/generate streaming endpoint.

    Falls back gracefully if Ollama is unreachable so the canned Layer-1
    path stays in effect.
    """
    # Prepend the conversation transcript so the model has recent context.
    full_prompt = prompt
    if transcript:
        full_prompt = f"Recent conversation:\n{transcript}\n\nUser: {prompt}"

    payload = {
        "model": _OLLAMA_MODEL,
        "prompt": full_prompt,
        "stream": True,
    }
    if system_prompt:
        payload["system"] = system_prompt
    try:
        with requests.post(
            f"{_OLLAMA_URL}/api/generate",
            json=payload,
            stream=True,
            timeout=_OLLAMA_TIMEOUT,
        ) as r:
            r.raise_for_status()
            for line in r.iter_lines():
                if not line:
                    continue
                try:
                    data = json.loads(line.decode("utf-8"))
                except Exception:
                    continue
                if "response" in data:
                    yield data["response"]
                if data.get("done"):
                    break
    except Exception as e:
        # Surface the error to the console but don't crash the loop.
        print(f"[CI-LLM] ollama call failed: {e}")
        return


def route_intent(text: str):

    t = text.lower()

    # -------------------------
    # MODE SWITCH
    # -------------------------
    if "playful mode" in t:
        engine.mode = "playful"
        return "Switched to playful mode."

    if "jarvis" in t:
        engine.mode = "jarvis"
        return "Jarvis mode activated."

    if "jarvis mode" in t:
        engine.mode = "jarvis"
        return "Switched to jarvis mode."

    if "assistant" in t:
        engine.mode = "assistant"
        return "Assistant mode activated."

    if "assistant mode" in t:
        engine.mode = "assistant"
        return "Switched to assistant mode."

    # -------------------------
    # HOLIDAYS
    # -------------------------

    if "january" in t:
        return get_holidays("january")

    if "february" in t:
        return get_holidays("february")

    if "march" in t:
        return get_holidays("march")

    if "april" in t:
        return get_holidays("april")

    if "may" in t:
        return get_holidays("may")

    if "june" in t:
        return get_holidays("june")

    if "july" in t:
        return get_holidays("july")

    if "august" in t:
        return get_holidays("august")

    if "september" in t:
        return get_holidays("september")

    if "october" in t:
        return get_holidays("october")

    if "november" in t:
        return get_holidays("november")

    if "december" in t:
        return get_holidays("december")

    if "bye" in t:
        if engine.mode == "playful":
            return "Haha 😄 See you next time!"
        elif engine.mode == "assistant":
            return "Goodbye! Let me know if you need anything else."
        else:
            return "Goodbye!"

    # Word-boundary checks below: avoid "times" -> "time" and "byebye" -> "bye"
    # style substring collisions. Holidays stay as substring matches because
    # the words ("june", "july", etc.) are very rarely substrings of other
    # common words, and tightening them would break "what's in june" style.
    if re.search(r"\btime\b", t):
        import time
        return f"The current time is {time.strftime('%H:%M:%S')}."

    if re.search(r"\b(date|today)\b", t):
        return "Today is Sunday, June 21, 2026."

    if re.search(r"\bjoke\b", t):
        if engine.mode == "playful":
            return "😄 Why did the AI cross the road? For fun!"
        return "Why did the AI cross the road? To optimize the reward function."


def stream_response(text: str, system_prompt=None, context=None):

    engine.update(text)

    # ❗ IMPORTANT: ONLY CALL route_intent ONCE
    response = route_intent(text)

    # Layer 1 hit (canned intent) — record both sides of the turn and stop.
    if response:
        _mem_push("user", text)
        _mem_push("assistant", response)
        yield response
        return

    # Layer 2: real LLM call to Ollama. Stream tokens as they arrive.
    if not system_prompt:
        try:
            system_prompt = engine.system_prompt()
        except Exception:
            system_prompt = "You are Jarvis, a calm and efficient AI assistant."

    # Strengthen the system prompt so the model admits ignorance rather than
    # hallucinating context it does not have.
    full_system = (
        system_prompt.strip()
        + "\n\nIf the user asks about something you do not know or cannot "
        "recall from the recent conversation, say so briefly. Never invent "
        "prior topics, prior user statements, or events that did not happen."
    )

    transcript = _mem_render()
    _mem_push("user", text)

    # Buffer the streamed response so we can record it in memory *after* the
    # full answer is known. We yield progressively to keep TTS latency low.
    collected: list[str] = []
    for chunk in _llm_stream(text, full_system, transcript=transcript):
        if chunk:
            collected.append(chunk)
            yield chunk

    if collected:
        _mem_push("assistant", "".join(collected))
    else:
        # LLM produced nothing — fall back to a mode-aware canned line and
        # record it so subsequent turns have something to reference.
        mode = engine.mode
        if mode == "playful":
            fb = "I'm having trouble reaching my brain right now, but I'm still here!"
        elif mode == "assistant":
            fb = "I'm sorry, I couldn't reach the language model. Please try again."
        else:
            fb = "My language model is unreachable at the moment, sir."
        _mem_push("assistant", fb)
        yield fb