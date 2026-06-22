from __future__ import annotations

import argparse
import sys
from pathlib import Path

from oopsql.config import load_config_file, write_default_config
from oopsql.formatter import format_reports
from oopsql.models import RiskReport, Severity
from oopsql.scanner import scan_path
from oopsql.sqlserver import format_connection_info, test_connection


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
        choices=["text", "json", "markdown"],
        default="text",
        help="Output format.",
    )
    scan.add_argument(
        "--config",
        type=Path,
        help="Path to an oopsql.yml file. Defaults to searching from the scan path.",
    )
    scan.add_argument(
        "--min-severity",
        choices=["LOW", "MEDIUM", "HIGH", "CRITICAL"],
        default="LOW",
        help="Only show findings at or above this severity.",
    )
    scan.add_argument(
        "--fail-on",
        choices=["LOW", "MEDIUM", "HIGH", "CRITICAL", "NONE"],
        default="LOW",
        help="Return exit code 1 when findings at or above this severity exist.",
    )

    connect = subparsers.add_parser(
        "connect",
        help="Test a SQL Server connection. This does not run SQL files.",
    )
    connect.add_argument(
        "--connection-string",
        required=True,
        help="ODBC connection string for the SQL Server you use in SSMS.",
    )
    connect.add_argument(
        "--timeout",
        type=int,
        default=5,
        help="Connection timeout in seconds.",
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
            config = load_config_file(args.config) if args.config else None
            reports = scan_path(args.path, config)
            reports = filter_reports(reports, args.min_severity)
            print(format_reports(reports, args.format))
            return 1 if should_fail(reports, args.fail_on) else 0

        if args.command == "connect":
            info = test_connection(args.connection_string, timeout=args.timeout)
            print(format_connection_info(info))
            return 0
    except Exception as exc:
        print(f"oopsql: {exc}", file=sys.stderr)
        return 2

    parser.print_help()
    return 2


def filter_reports(reports: list[RiskReport], min_severity: str) -> list[RiskReport]:
    threshold = Severity[min_severity]
    filtered: list[RiskReport] = []
    for report in reports:
        findings = [
            finding
            for finding in report.findings
            if Severity[finding.severity] >= threshold
        ]
        filtered.append(RiskReport(file=report.file, findings=findings))
    return filtered


def should_fail(reports: list[RiskReport], fail_on: str) -> bool:
    if fail_on == "NONE":
        return False
    threshold = Severity[fail_on]
    return any(
        Severity[finding.severity] >= threshold
        for report in reports
        for finding in report.findings
    )


if __name__ == "__main__":
    raise SystemExit(main())
