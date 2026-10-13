import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

from core.application import KissaneApplication
from core.models import EvidenceSignal


def load_signals(path):
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8-sig"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"Cannot read valid JSON: {exc}") from exc

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
            signal = EvidenceSignal(
                signal_id=item["signal_id"],
                title=item["title"],
                source_name=item["source_name"],
                source_url=item["source_url"],
                discovered_at=datetime.fromisoformat(timestamp.replace("Z", "+00:00")),
                description=item.get("description", ""),
                country_code=item.get("country_code"),
            )
            signals.append(signal)
        except (KeyError, TypeError, AttributeError, ValueError) as exc:
            raise ValueError(f"Invalid signal at index {index}: {exc}") from exc
    return signals


def build_parser():
    parser = argparse.ArgumentParser(description="KISSANE")
    parser.add_argument("--database", default=None, help="SQLite database path")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("status", help="Show application status")
    commands.add_parser("list", help="List stored signals")
    ingest = commands.add_parser("ingest-json", help="Import signals from JSON")
    ingest.add_argument("file", help="JSON file path")
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
