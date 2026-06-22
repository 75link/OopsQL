from __future__ import annotations

import re


def preview_template(statement: str) -> str | None:
    normalized = " ".join(statement.strip().split())
    if re.match(r"(?is)^update\b", normalized):
        return _update_preview(statement)
    if re.match(r"(?is)^delete\b", normalized):
        return _delete_preview(statement)
    return None


def _update_preview(statement: str) -> str | None:
    table_match = re.search(r"(?is)^\s*update\s+(?:top\s*\([^)]+\)\s+)?([#[\]\w.]+)", statement)
    where_match = re.search(r"(?is)\bwhere\b\s+(.+?)(?:;|\s*$)", statement)
    if not table_match or not where_match:
        return None

    table = table_match.group(1)
    where_clause = where_match.group(1).strip()
    sql = statement.strip().rstrip(";")
    return (
        "BEGIN TRAN;\n\n"
        "SELECT *\n"
        f"FROM {table}\n"
        f"WHERE {where_clause};\n\n"
        f"{sql};\n\n"
        "-- Check @@ROWCOUNT before committing\n"
        "-- COMMIT;\n"
        "-- ROLLBACK;"
    )


def _delete_preview(statement: str) -> str | None:
    table_match = re.search(r"(?is)^\s*delete\s+(?:from\s+)?([#[\]\w.]+)", statement)
    where_match = re.search(r"(?is)\bwhere\b\s+(.+?)(?:;|\s*$)", statement)
    if not table_match or not where_match:
        return None

    table = table_match.group(1)
    where_clause = where_match.group(1).strip()
    sql = statement.strip().rstrip(";")
    return (
        "BEGIN TRAN;\n\n"
        "SELECT *\n"
        f"FROM {table}\n"
        f"WHERE {where_clause};\n\n"
        f"{sql};\n\n"
        "-- Check @@ROWCOUNT before committing\n"
        "-- COMMIT;\n"
        "-- ROLLBACK;"
    )

