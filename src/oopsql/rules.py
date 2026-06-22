from __future__ import annotations

import re
from dataclasses import dataclass

from oopsql.config import OopsConfig
from oopsql.models import Finding
from oopsql.suggestions import preview_template


@dataclass(frozen=True)
class SqlStatement:
    text: str
    line: int

    @property
    def excerpt(self) -> str:
        one_line = " ".join(self.text.strip().split())
        return one_line[:240]


def analyze_sql(sql: str, config: OopsConfig) -> list[Finding]:
    statements = split_statements(sql)
    findings: list[Finding] = []

    for statement in statements:
        findings.extend(_statement_findings(statement, config))

    findings.extend(_file_findings(sql, statements, config))
    return sorted(
        findings,
        key=lambda finding: (
            finding.line if finding.line is not None else 10**9,
            finding.rule_id,
        ),
    )


def split_statements(sql: str) -> list[SqlStatement]:
    statements: list[SqlStatement] = []
    buffer: list[str] = []
    start_line: int | None = None
    in_single_quote = False
    in_bracket = False
    line = 1

    for char in sql:
        if start_line is None and not char.isspace():
            start_line = line

        buffer.append(char)

        if char == "\n":
            line += 1
        elif char == "'" and not in_bracket:
            in_single_quote = not in_single_quote
        elif char == "[" and not in_single_quote:
            in_bracket = True
        elif char == "]" and not in_single_quote:
            in_bracket = False
        elif char == ";" and not in_single_quote and not in_bracket:
            _append_statement(statements, buffer, start_line)
            buffer = []
            start_line = None

    _append_statement(statements, buffer, start_line)
    return statements


def _append_statement(
    statements: list[SqlStatement], buffer: list[str], start_line: int | None
) -> None:
    text = "".join(buffer).strip()
    if text:
        statements.append(SqlStatement(text=text, line=start_line or 1))


def _statement_findings(statement: SqlStatement, config: OopsConfig) -> list[Finding]:
    text = _strip_leading_comments(statement.text)
    findings: list[Finding] = []

    if _starts_with(text, "UPDATE") and not _has_word(text, "WHERE"):
        findings.append(
            Finding(
                rule_id="OOPS001",
                severity="CRITICAL",
                line=statement.line,
                excerpt=statement.excerpt,
                message="UPDATE statement detected without a WHERE clause.",
                suggestion=(
                    "Add a WHERE clause, run a SELECT preview first, and wrap the "
                    "change in a transaction."
                ),
            )
        )

    if _starts_with(text, "DELETE") and not _has_word(text, "WHERE"):
        findings.append(
            Finding(
                rule_id="OOPS002",
                severity="CRITICAL",
                line=statement.line,
                excerpt=statement.excerpt,
                message="DELETE statement detected without a WHERE clause.",
                suggestion=(
                    "Add a WHERE clause, run a SELECT preview first, and wrap the "
                    "change in a transaction."
                ),
            )
        )

    if re.search(r"(?is)\btruncate\s+table\b", text):
        findings.append(
            Finding(
                rule_id="OOPS003",
                severity="CRITICAL",
                line=statement.line,
                excerpt=statement.excerpt,
                message="TRUNCATE TABLE statement detected.",
                suggestion="Confirm this is intentional and require an approved recovery plan.",
            )
        )

    if _starts_with(text, "DROP"):
        findings.append(
            Finding(
                rule_id="OOPS004",
                severity="CRITICAL",
                line=statement.line,
                excerpt=statement.excerpt,
                message="DROP statement detected.",
                suggestion="Avoid destructive schema changes without review, backup, and rollback steps.",
            )
        )

    if _starts_with(text, "ALTER"):
        findings.append(
            Finding(
                rule_id="OOPS005",
                severity="HIGH",
                line=statement.line,
                excerpt=statement.excerpt,
                message="ALTER statement detected.",
                suggestion="Review schema impact and deployment order before running ALTER statements.",
            )
        )

    if _starts_with(text, "MERGE"):
        findings.append(
            Finding(
                rule_id="OOPS006",
                severity="HIGH",
                line=statement.line,
                excerpt=statement.excerpt,
                message="MERGE statement detected.",
                suggestion="Validate match conditions and test for duplicate matches before execution.",
            )
        )

    if re.search(r"(?is)\bselect\s+\*", text):
        findings.append(
            Finding(
                rule_id="OOPS008",
                severity="MEDIUM",
                line=statement.line,
                excerpt=statement.excerpt,
                message="SELECT * detected.",
                suggestion="Select explicit columns to reduce accidental data exposure and query drift.",
            )
        )

    if re.search(r"(?is)\bwith\s*\(\s*nolock\s*\)|\bnolock\b", text):
        findings.append(
            Finding(
                rule_id="OOPS009",
                severity="MEDIUM",
                line=statement.line,
                excerpt=statement.excerpt,
                message="NOLOCK hint detected.",
                suggestion="Avoid dirty reads unless the reporting risk is understood and accepted.",
            )
        )

    for table in _protected_tables_touched(text, config):
        findings.append(
            Finding(
                rule_id="OOPS010",
                severity="HIGH",
                line=statement.line,
                excerpt=statement.excerpt,
                message=f"The script touches protected table: {table}.",
                suggestion="Require review before modifying protected business data.",
            )
        )

    if _possible_one_to_many_reporting_join(text):
        findings.append(
            Finding(
                rule_id="OOPS012",
                severity="MEDIUM",
                line=statement.line,
                excerpt=statement.excerpt,
                message="Possible one-to-many reporting join risk detected.",
                suggestion=(
                    "Check join grain and aggregate after pre-aggregating child tables to "
                    "avoid duplicated totals."
                ),
            )
        )

    preview = preview_template(statement.text)
    if preview:
        preview_excerpt = f"{statement.excerpt}\n\nSuggested preview:\n{preview}"
        findings = [_replace_excerpt(finding, preview_excerpt) for finding in findings]

    return findings


def _file_findings(
    sql: str, statements: list[SqlStatement], config: OopsConfig
) -> list[Finding]:
    findings: list[Finding] = []
    risky_statement = next(
        (
            statement
            for statement in statements
            if _is_transaction_required(statement.text, config)
        ),
        None,
    )
    if risky_statement and not re.search(r"(?is)\bbegin\s+(tran|transaction)\b", sql):
        findings.append(
            Finding(
                rule_id="OOPS007",
                severity="HIGH",
                line=risky_statement.line,
                excerpt=risky_statement.excerpt,
                message="Risky data-changing statement detected without BEGIN TRAN.",
                suggestion="Use BEGIN TRAN, verify @@ROWCOUNT, then COMMIT or ROLLBACK.",
            )
        )

    if _has_risky_script_content(statements) and not re.search(
        r"(?is)\brollback\b|rollback\s+plan|rollback\s+section", sql
    ):
        first_line = statements[0].line if statements else None
        findings.append(
            Finding(
                rule_id="OOPS011",
                severity="MEDIUM",
                line=first_line,
                message="No rollback section/comment found.",
                suggestion="Add a rollback plan before production execution.",
            )
        )

    return findings


def _strip_leading_comments(text: str) -> str:
    cleaned = text.strip()
    while True:
        next_cleaned = re.sub(r"(?is)^--[^\n]*(?:\n|$)", "", cleaned).strip()
        next_cleaned = re.sub(r"(?is)^/\*.*?\*/", "", next_cleaned).strip()
        if next_cleaned == cleaned:
            return cleaned
        cleaned = next_cleaned


def _starts_with(text: str, keyword: str) -> bool:
    return re.match(rf"(?is)^\s*{re.escape(keyword)}\b", text) is not None


def _has_word(text: str, word: str) -> bool:
    return re.search(rf"(?is)\b{re.escape(word)}\b", text) is not None


def _protected_tables_touched(text: str, config: OopsConfig) -> list[str]:
    touched: list[str] = []
    for table in config.protected_tables:
        pattern = rf"(?is)(?:\b\w+\s*\.\s*)?\b{re.escape(table)}\b"
        if re.search(pattern, text) and table not in touched:
            touched.append(table)
    return touched


def _possible_one_to_many_reporting_join(text: str) -> bool:
    if not _starts_with(text, "SELECT"):
        return False
    has_join = re.search(r"(?is)\bjoin\b", text) is not None
    has_aggregate = re.search(r"(?is)\b(sum|count|avg|min|max)\s*\(", text) is not None
    childish_name = re.search(
        r"(?is)\b(invoiceitem|line|lines|detail|details|item|items|entry|entries)\b",
        text,
    )
    has_group_by = re.search(r"(?is)\bgroup\s+by\b", text) is not None
    return has_join and (has_aggregate or childish_name is not None) and not has_group_by


def _is_transaction_required(text: str, config: OopsConfig) -> bool:
    cleaned = _strip_leading_comments(text)
    for keyword in config.require_transaction_for:
        if keyword == "TRUNCATE":
            if re.search(r"(?is)^\s*truncate\s+table\b", cleaned):
                return True
        elif _starts_with(cleaned, keyword):
            return True
    return False


def _has_risky_script_content(statements: list[SqlStatement]) -> bool:
    return any(
        re.match(
            r"(?is)^\s*(update|delete|merge|insert|alter|drop|truncate)\b",
            _strip_leading_comments(statement.text),
        )
        for statement in statements
    )


def _replace_excerpt(finding: Finding, excerpt: str) -> Finding:
    return Finding(
        rule_id=finding.rule_id,
        severity=finding.severity,
        line=finding.line,
        message=finding.message,
        suggestion=finding.suggestion,
        excerpt=excerpt,
    )
