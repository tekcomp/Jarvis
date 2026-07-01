"""Quick interactive query/filter for logs/transcript.log.

Usage:
    python tools/transcript_filter.py --since 01:30
    python tools/transcript_filter.py --intent joke
    python tools/transcript_filter.py --user-only
    python tools/transcript_filter.py --jarvis-only --since 01:00
    python tools/transcript_filter.py --text "teal"
    python tools/transcript_filter.py --count

Combines freely. Defaults to last 24 hours if no --since is given.
"""
import argparse
import re
import sys
from datetime import datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_LOG = ROOT / "logs" / "transcript.log"


def _parse_line(line: str):
    line = line.rstrip("\n").rstrip("\r")
    if not line:
        return None
    parts = line.split(" ", 1)
    if len(parts) != 2:
        return None
    ts, body = parts
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


def _since_ok(ts: str, since_dt: datetime | None) -> bool:
    if since_dt is None:
        return True
    try:
        return datetime.fromisoformat(ts) >= since_dt
    except ValueError:
        return True


def _resolve_since(since_arg: str | None, last_hours: int | None) -> datetime | None:
    if since_arg:
        try:
            if "T" in since_arg:
                return datetime.fromisoformat(since_arg)
            today = datetime.now().date().isoformat()
            return datetime.fromisoformat(f"{today}T{since_arg}")
        except ValueError:
            print(f"  bad --since format: {since_arg!r}", file=sys.stderr)
            sys.exit(2)
    if last_hours:
        return datetime.now() - timedelta(hours=last_hours)
    return None


def main() -> int:
    parser = argparse.ArgumentParser(description="Filter logs/transcript.log")
    parser.add_argument("--log", default=str(DEFAULT_LOG))
    parser.add_argument("--since", help="HH:MM or YYYY-MM-DDTHH:MM")
    parser.add_argument("--last-hours", type=int, help="Last N hours (default 24 if no --since)")
    parser.add_argument("--intent", help="Filter by intent tag (joke, time, llm, ...)")
    parser.add_argument("--user-only", action="store_true")
    parser.add_argument("--jarvis-only", action="store_true")
    parser.add_argument("--text", help="Substring match against the line text")
    parser.add_argument("--regex", help="Regex match against the line text")
    parser.add_argument("--count", action="store_true", help="Just print the count")
    parser.add_argument("--limit", type=int, default=50, help="Max lines to print")
    args = parser.parse_args()

    if args.user_only and args.jarvis_only:
        print("  --user-only and --jarvis-only are mutually exclusive", file=sys.stderr)
        return 2

    log_path = Path(args.log)
    if not log_path.exists():
        print(f"  log file not found: {log_path}", file=sys.stderr)
        return 1

    since_dt = _resolve_since(args.since, args.last_hours)
    if since_dt and not args.since and not args.last_hours:
        # Default to last 24 hours when nothing is specified.
        since_dt = datetime.now() - timedelta(hours=24)
        print(f"  (no --since given; defaulting to last 24 hours, since={since_dt.isoformat(timespec='seconds')})")

    text_sub = args.text.lower() if args.text else None
    text_re = re.compile(args.regex, re.IGNORECASE) if args.regex else None

    matched = []
    with log_path.open("r", encoding="utf-8") as f:
        for line in f:
            parsed = _parse_line(line)
            if not parsed:
                continue
            ts, intent, role, text = parsed
            if not _since_ok(ts, since_dt):
                continue
            if args.intent and intent != args.intent:
                continue
            if args.user_only and role != "USER":
                continue
            if args.jarvis_only and role != "JARVIS":
                continue
            if text_sub and text_sub not in text.lower():
                continue
            if text_re and not text_re.search(text):
                continue
            matched.append((ts, intent, role, text))

    print(f"  matched {len(matched)} line(s)")
    if args.count:
        return 0
    for ts, intent, role, text in matched[: args.limit]:
        tag = f"[{intent}]" if intent else ""
        short = text if len(text) <= 110 else text[:107] + "..."
        print(f"    {ts} {tag}{role}: {short}")
    if len(matched) > args.limit:
        print(f"    ... and {len(matched) - args.limit} more (use --limit to see more)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
