import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

from core.application import KissaneApplication
from core.models import EvidenceSignal
from input.rss_collector import fetch_rss
from processor.opportunity_scorer import score_signal


def load_signals(path):
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8-sig"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError("Cannot read valid JSON: {}".format(exc)) from exc
    if not isinstance(data, list):
        raise ValueError("JSON root must be a list")
    signals = []
    for index, item in enumerate(data):
        try:
            if not isinstance(item, dict):
                raise ValueError("expected a JSON object")
            timestamp = item["discovered_at"]
            if not isinstance(timestamp, str):
                raise ValueError("discovered_at must be a string")
            signals.append(EvidenceSignal(
                signal_id=item["signal_id"],
                title=item["title"],
                source_name=item["source_name"],
                source_url=item["source_url"],
                discovered_at=datetime.fromisoformat(timestamp.replace("Z", "+00:00")),
                description=item.get("description", ""),
                country_code=item.get("country_code"),
            ))
        except (KeyError, TypeError, AttributeError, ValueError) as exc:
            raise ValueError("Invalid signal at index {}: {}".format(index, exc)) from exc
    return signals


def build_parser():
    parser = argparse.ArgumentParser(description="KISSANE")
    parser.add_argument("--database", default=None, help="SQLite database path")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("status", help="Show application status")
    commands.add_parser("list", help="List stored signals")
    commands.add_parser("rank", help="Rank stored signals by commercial relevance")
    ingest = commands.add_parser("ingest-json", help="Import signals from JSON")
    ingest.add_argument("file", help="JSON file path")
    rss = commands.add_parser("fetch-rss", help="Fetch an RSS/Atom feed and store entries")
    rss.add_argument("url", help="RSS or Atom feed URL")
    rss.add_argument("--limit", type=int, default=20, help="Maximum entries to import (1-100)")
    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)
    try:
        if args.command == "ingest-json":
            signals = load_signals(args.file)
            with KissaneApplication(args.database) as app:
                report = app.process_signals(signals)
                print("Processed {} unique signal(s).".format(report["count"]))
                print("Stored total: {}".format(len(app.list_signals())))
        elif args.command == "fetch-rss":
            if not 1 <= args.limit <= 100:
                raise ValueError("limit must be between 1 and 100")
            signals = fetch_rss(args.url, limit=args.limit)
            with KissaneApplication(args.database) as app:
                report = app.process_signals(signals)
                print("Fetched {} signal(s).".format(len(signals)))
                print("Processed {} unique signal(s).".format(report["count"]))
                print("Stored total: {}".format(len(app.list_signals())))
        elif args.command == "rank":
            with KissaneApplication(args.database) as app:
                ranked = [score_signal(signal) for signal in app.list_signals()]
                ranked.sort(key=lambda item: item["score"], reverse=True)
                if not ranked:
                    print("No signals stored yet.")
                for item in ranked:
                    reason = "; ".join(item["reasons"])
                    print("{} | {} | {} | {}".format(item["score"], item["category"], item["title"], reason))
        else:
            with KissaneApplication(args.database) as app:
                signals = app.list_signals()
                if args.command == "status":
                    print("KISSANE status: OK")
                    print("Database: {}".format(app.database_path))
                    print("Stored signals: {}".format(len(signals)))
                elif not signals:
                    print("No signals stored yet.")
                else:
                    for signal in signals:
                        print("{} | {} | {} | {}".format(signal.signal_id, signal.title, signal.source_name, signal.source_url))
        return 0
    except (ValueError, TypeError, RuntimeError) as exc:
        print("Error: {}".format(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())

