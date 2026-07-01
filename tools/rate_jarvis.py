"""Retroactively rate a JARVIS response in logs/transcript.log.

Usage:
    python tools/rate_jarvis.py                    # rate the most recent JARVIS line
    python tools/rate_jarvis.py --ts 01:30:00     # rate the line closest to that time today
    python tools/rate_jarvis.py --value 1         # thumbs up
    python tools/rate_jarvis.py --value -1        # thumbs down
    python tools/rate_jarvis.py --value 0         # neutral

Side effect: appends a "<ts> RATING: <value> [comment]" line to
logs/transcript.log. The JSONL extractor will pick this up and attach
the rating to the most recent JARVIS line.

Note: this CLI is independent of the live kernel — you can run it while
Jarvis is offline, or against an old transcript.log from yesterday.
"""
import argparse
import datetime
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LOG = ROOT / "logs" / "transcript.log"


def _read_log() -> list[str]:
    if not LOG.exists():
        return []
    return LOG.read_text(encoding="utf-8").splitlines()


def _last_jarvis_ts(log_lines: list[str]) -> str | None:
    """Return the ISO timestamp of the most recent JARVIS line."""
    for line in reversed(log_lines):
        parts = line.split(" ", 1)
        if len(parts) != 2:
            continue
        body = parts[1]
        # Strip optional [tag] prefix.
        if body.startswith("["):
            end = body.find("]")
            if end > 0:
                body = body[end + 1:].lstrip()
        if body.startswith("JARVIS:"):
            return parts[0]
    return None


def _ts_for_today(hh_mm: str) -> str | None:
    try:
        today = datetime.date.today().isoformat()
        return f"{today}T{hh_mm}:00"
    except ValueError:
        return None


def _ts_closest_to(log_lines: list[str], target: str) -> str | None:
    try:
        target_dt = datetime.datetime.fromisoformat(target)
    except ValueError:
        return None
    best = None
    best_diff = None
    for line in log_lines:
        parts = line.split(" ", 1)
        if len(parts) != 2 or not parts[0].startswith("20"):
            continue
        body = parts[1]
        if body.startswith("["):
            end = body.find("]")
            if end > 0:
                body = body[end + 1:].lstrip()
        if not body.startswith("JARVIS:"):
            continue
        try:
            line_dt = datetime.datetime.fromisoformat(parts[0])
        except ValueError:
            continue
        diff = abs((line_dt - target_dt).total_seconds())
        if best_diff is None or diff < best_diff:
            best = parts[0]
            best_diff = diff
    return best


def main() -> int:
    parser = argparse.ArgumentParser(description="Rate a JARVIS response in the transcript")
    parser.add_argument("--value", "-v", type=int, choices=[-1, 0, 1],
                        help="-1, 0, or +1. If omitted, prompts on stdin.")
    parser.add_argument("--comment", "-c", default="", help="Optional comment text")
    parser.add_argument("--ts", help="HH:MM today, or full ISO-8601 timestamp")
    parser.add_argument("--last", action="store_true",
                        help="Rate the most recent JARVIS line (default if --ts is omitted)")
    args = parser.parse_args()

    value = args.value
    if value is None:
        try:
            raw = input("Rating (-1 / 0 / +1): ").strip()
        except EOFError:
            print("  no value provided; pass --value", file=sys.stderr)
            return 2
        try:
            value = int(raw)
        except ValueError:
            print(f"  invalid rating {raw!r}", file=sys.stderr)
            return 2
        if value not in (-1, 0, 1):
            print(f"  rating must be -1, 0, or 1, got {value}", file=sys.stderr)
            return 2

    log_lines = _read_log()
    if not log_lines:
        print(f"  log file empty or missing: {LOG}", file=sys.stderr)
        return 1

    if args.ts:
        # Could be HH:MM (today) or full ISO-8601.
        target = args.ts if "T" in args.ts else _ts_for_today(args.ts)
        if target is None:
            print(f"  bad --ts format: {args.ts!r}", file=sys.stderr)
            return 2
        ts = _ts_closest_to(log_lines, target)
    else:
        ts = _last_jarvis_ts(log_lines)

    if ts is None:
        print("  no JARVIS line found in the transcript", file=sys.stderr)
        return 1

    # Append the rating line.
    now = datetime.datetime.now().isoformat(timespec="seconds")
    comment = args.comment.strip()
    suffix = f" {comment}" if comment else ""
    line = f"{now} RATING: {value:+d}{suffix}\n"
    LOG.parent.mkdir(parents=True, exist_ok=True)
    with LOG.open("a", encoding="utf-8") as f:
        f.write(line)

    label = {1: "thumbs up", 0: "neutral", -1: "thumbs down"}[value]
    print(f"  {label} (rating={value:+d}) recorded for JARVIS line at {ts}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
