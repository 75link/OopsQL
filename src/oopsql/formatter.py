from __future__ import annotations

import json

from oopsql.models import RiskReport, Severity


def format_reports(reports: list[RiskReport], output_format: str = "text") -> str:
    if output_format == "json":
        payload: object
        if len(reports) == 1:
            payload = reports[0].to_dict()
        else:
            payload = {
                "files_count": len(reports),
                "overall_risk": _overall_risk(reports),
                "findings_count": sum(report.findings_count for report in reports),
                "reports": [report.to_dict() for report in reports],
            }
        return json.dumps(payload, indent=2)

    if output_format == "markdown":
        return format_markdown_reports(reports)

    return "\n\n".join(format_text_report(report) for report in reports)


def format_text_report(report: RiskReport) -> str:
    lines = [
        "OopsQL Risk Report",
        f"File: {report.file}",
        "",
        f"Overall Risk: {report.overall_risk}",
        f"Findings: {report.findings_count}",
    ]

    if not report.findings:
        lines.extend(["", "No risky patterns detected."])
        return "\n".join(lines)

    for finding in report.findings:
        lines.extend(
            [
                "",
                f"[{finding.severity}] {finding.rule_id} - {_title_for(finding.rule_id)}",
            ]
        )
        if finding.line is not None:
            lines.append(f"Line: {finding.line}")
        lines.append(f"Message: {finding.message}")
        if finding.excerpt:
            lines.append(f"Excerpt: {finding.excerpt}")
        lines.append(f"Suggestion: {finding.suggestion}")

    return "\n".join(lines)


def format_markdown_reports(reports: list[RiskReport]) -> str:
    lines = [
        "# OopsQL Risk Report",
        "",
        f"Overall risk: **{_overall_risk(reports)}**",
        f"Files scanned: **{len(reports)}**",
        f"Findings: **{sum(report.findings_count for report in reports)}**",
    ]

    for report in reports:
        lines.extend(
            [
                "",
                f"## {report.file}",
                "",
                f"Overall risk: **{report.overall_risk}**",
                f"Findings: **{report.findings_count}**",
            ]
        )
        if not report.findings:
            lines.extend(["", "No risky patterns detected."])
            continue

        lines.extend(
            [
                "",
                "| Severity | Rule | Line | Message |",
                "| --- | --- | --- | --- |",
            ]
        )
        for finding in report.findings:
            line = "" if finding.line is None else str(finding.line)
            lines.append(
                "| "
                f"{finding.severity} | {finding.rule_id} | {line} | "
                f"{_escape_markdown_cell(finding.message)} |"
            )

    return "\n".join(lines)


def _overall_risk(reports: list[RiskReport]) -> str:
    if not reports:
        return "LOW"
    return max(reports, key=lambda report: Severity[report.overall_risk]).overall_risk


def _escape_markdown_cell(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ")


def _title_for(rule_id: str) -> str:
    titles = {
        "OOPS001": "UPDATE without WHERE",
        "OOPS002": "DELETE without WHERE",
        "OOPS003": "TRUNCATE TABLE detected",
        "OOPS004": "DROP statement detected",
        "OOPS005": "ALTER statement detected",
        "OOPS006": "MERGE statement detected",
        "OOPS007": "Missing transaction",
        "OOPS008": "SELECT * detected",
        "OOPS009": "NOLOCK detected",
        "OOPS010": "Protected table touched",
        "OOPS011": "Missing rollback section",
        "OOPS012": "Possible one-to-many reporting join risk",
    }
    return titles.get(rule_id, "Risk detected")
