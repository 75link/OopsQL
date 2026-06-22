from __future__ import annotations

import argparse
import sys
from pathlib import Path

from oopsql.config import write_default_config
from oopsql.formatter import format_reports
from oopsql.scanner import scan_path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="oopsql",
        description="Analyze T-SQL scripts for production blast-radius risks.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    scan = subparsers.add_parser("scan", help="Scan a .sql file or folder.")
    scan.add_argument("path", type=Path, help="Path to a .sql file or folder.")
    scan.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format.",
    )

    subparsers.add_parser("init-config", help="Create an oopsql.yml config file.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        if args.command == "init-config":
            write_default_config(Path.cwd() / "oopsql.yml")
            print("Created oopsql.yml")
            return 0

        if args.command == "scan":
            reports = scan_path(args.path)
            print(format_reports(reports, args.format))
            return 1 if any(report.findings for report in reports) else 0
    except Exception as exc:
        print(f"oopsql: {exc}", file=sys.stderr)
        return 2

    parser.print_help()
    return 2


if __name__ == "__main__":
    raise SystemExit(main())

