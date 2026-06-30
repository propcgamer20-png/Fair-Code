"""Command-line interface for the Fair Code dataset profiler.

    faircode profile data.csv
    faircode profile data.csv --json
    faircode profile data.csv --html report.html

Uses only stdlib argparse + pandas (no heavyweight profiling dependency).
"""

from __future__ import annotations

import argparse
import sys

import pandas as pd

from . import __version__
from .profiler import profile
from .report import to_html, to_json, to_terminal


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="faircode",
        description="Audit a tabular dataset for demographic representation.",
    )
    parser.add_argument("--version", action="version",
                        version=f"faircode {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("profile", help="profile a CSV for demographic imbalance")
    p.add_argument("csv", help="path to the CSV file")
    p.add_argument("--json", action="store_true", help="emit JSON to stdout")
    p.add_argument("--html", metavar="PATH",
                   help="write a standalone HTML report to PATH")

    args = parser.parse_args(argv)

    if args.command == "profile":
        try:
            df = pd.read_csv(args.csv)
        except FileNotFoundError:
            print(f"error: file not found: {args.csv}", file=sys.stderr)
            return 2
        except Exception as exc:  # noqa: BLE001 - surface any parse failure plainly
            print(f"error: could not read CSV: {exc}", file=sys.stderr)
            return 2

        result = profile(df)

        if args.html:
            with open(args.html, "w", encoding="utf-8") as fh:
                fh.write(to_html(result))
            print(f"HTML report written to {args.html}", file=sys.stderr)

        if args.json:
            print(to_json(result))
        else:
            print(to_terminal(result))
        return 0

    parser.print_help()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
