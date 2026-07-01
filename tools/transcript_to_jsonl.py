"""Convert logs/transcript.log into a JSONL training dataset.

Pairs each USER line with the next JARVIS line. Output: one JSON object
per line, ready for fine-tuning (OpenAI/Anthropic/Alpaca/ShareGPT style).

Usage:
    python tools/transcript_to_jsonl.py
    python tools/transcript_to_jsonl.py --since 14:00
    python tools/transcript_to_jsonl.py --output data\my_pairs.jsonl
    python tools/transcript_to_jsonl.py --intent joke          # only joke exchanges
    python tools/transcript_to_jsonl.py --min-turns 2         # require N+ pairs

Output schema (OpenAI chat fine-tuning style):
    {"messages": [
        {"role": "user",      "content": "jarvis what time is it"},
        {"role": "assistant", "content": "The current time is 01:30:00."}
    ], "intent": "time", "timestamp": "2026-07-01T01:30:00"}

Run from repo root.
"""
import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_LOG = ROOT / "logs" / "transcript.log"
DEFAULT_OUT = ROOT / "data" / "transcript_pairs.jsonl"


def _parse_line(line: str):
    """Parse a transcript line. Returns (timestamp, intent, role, text) or None."""
    line = line.rstrip("\n").rstrip("\r")
    if not line:
        return None
    # Expected: "2026-07-01T01:33:43 [intent] ROLE: text"
    parts = line.split(" ", 1)
    if len(parts) != 2:
        return None
    ts, body = parts
    # Validate timestamp shape.
    try:
        datetime.strptime(ts, "%Y-%m-%dT%H:%M:%S")
    except ValueError:
        return None
    intent = ""
    if body.startswith("["):
        end = body.find("]")
        if end > 0:
            intent = body[1:end]
            body = body[end + 1:].lstrip()
    role_end = body.find(":")
    if role_end < 0:
        return None
    role = body[:role_end]
    text = body[role_end + 1:].lstrip()
    if role not in ("USER", "JARVIS"):
        return None
    return ts, intent, role, text


def _since_ok(ts: str, since: str | None) -> bool:
    if not since:
        return True
    # Accept "HH:MM" or "YYYY-MM-DDTHH:MM".
    try:
        if ":" in since and "T" not in since:
            cutoff = datetime.fromisoformat(f"{ts[:10]}T{since}:00")
        else:
            cutoff = datetime.fromisoformat(since)
        return datetime.fromisoformat(ts) >= cutoff
    except ValueError:
        return True  # bad input -> don't filter


def extract(
    log_path: Path,
    since: str | None = None,
    intent_filter: str | None = None,
    max_pairs: int | None = None,
):
    """Yield (timestamp, intent, user_text, jarvis_text) tuples."""
    if not log_path.exists():
        print(f"  log file not found: {log_path}", file=sys.stderr)
        return
    pending = None  # (ts, intent, text) for the open USER turn
    pairs = 0
    with log_path.open("r", encoding="utf-8") as f:
        for line in f:
            parsed = _parse_line(line)
            if not parsed:
                continue
            ts, intent, role, text = parsed
            if not _since_ok(ts, since):
                continue
            if role == "USER":
                # Start a new pending turn. If a previous pending exists
                # without a JARVIS reply, drop it (no reply means the
                # kernel didn't act on it).
                pending = (ts, intent, text)
            elif role == "JARVIS" and pending is not None:
                pts, pintent, utext = pending
                # The intent tag for the JARVIS line is the one we want
                # for the pair. If the JARVIS line had no tag but the
                # USER did, fall back to that.
                pair_intent = intent or pintent
                if intent_filter and pair_intent != intent_filter:
                    pending = None
                    continue
                yield (pts, pair_intent, utext, text)
                pairs += 1
                pending = None
                if max_pairs is not None and pairs >= max_pairs:
                    return


def main() -> int:
    parser = argparse.ArgumentParser(description="Convert transcript.log to JSONL")
    parser.add_argument("--log", default=str(DEFAULT_LOG), help="Path to transcript.log")
    parser.add_argument("--output", default=str(DEFAULT_OUT), help="Output JSONL path")
    parser.add_argument("--since", default=None, help="Filter by HH:MM or YYYY-MM-DDTHH:MM")
    parser.add_argument("--intent", default=None, help="Only keep pairs with this intent tag")
    parser.add_argument("--max-pairs", type=int, default=None, help="Stop after N pairs")
    parser.add_argument("--dry-run", action="store_true", help="Don't write the output file")
    args = parser.parse_args()

    log_path = Path(args.log)
    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    pairs = list(extract(
        log_path,
        since=args.since,
        intent_filter=args.intent,
        max_pairs=args.max_pairs,
    ))

    if not pairs:
        print("  no pairs matched; nothing to write")
        return 0

    print(f"  extracted {len(pairs)} pair(s) from {log_path}")
    if args.dry_run:
        for ts, intent, u, j in pairs[:5]:
            preview_u = (u[:60] + "...") if len(u) > 60 else u
            preview_j = (j[:60] + "...") if len(j) > 60 else j
            tag = f"[{intent}]" if intent else "[no-tag]"
            print(f"    {ts} {tag}  U: {preview_u!r}  J: {preview_j!r}")
        if len(pairs) > 5:
            print(f"    ... and {len(pairs) - 5} more")
        return 0

    with out_path.open("w", encoding="utf-8") as f:
        for ts, intent, u, j in pairs:
            rec = {
                "messages": [
                    {"role": "user", "content": u},
                    {"role": "assistant", "content": j},
                ],
                "intent": intent,
                "timestamp": ts,
            }
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")

    print(f"  wrote {len(pairs)} pair(s) to {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
