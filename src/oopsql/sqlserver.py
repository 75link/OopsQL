from __future__ import annotations

from dataclasses import dataclass
from importlib import import_module
from typing import Any


class SqlServerError(RuntimeError):
    pass


@dataclass(frozen=True)
class SqlServerInfo:
    server_name: str
    database_name: str
    user_name: str
    server_version: str


def test_connection(connection_string: str, timeout: int = 5) -> SqlServerInfo:
    pyodbc = _load_pyodbc()
    try:
        connection = pyodbc.connect(connection_string, timeout=timeout)
        try:
            cursor = connection.cursor()
            row = cursor.execute(
                """
                SELECT
                  CONVERT(nvarchar(256), SERVERPROPERTY('ServerName')) AS server_name,
                  DB_NAME() AS database_name,
                  SUSER_SNAME() AS user_name,
                  CONVERT(nvarchar(256), SERVERPROPERTY('ProductVersion')) AS server_version
                """
            ).fetchone()
        finally:
            connection.close()
    except Exception as exc:
        raise SqlServerError(f"SQL Server connection failed: {exc}") from exc

    return SqlServerInfo(
        server_name=str(row.server_name),
        database_name=str(row.database_name),
        user_name=str(row.user_name),
        server_version=str(row.server_version),
    )


def format_connection_info(info: SqlServerInfo) -> str:
    return "\n".join(
        [
            "OopsQL SQL Server Connection",
            f"Server: {info.server_name}",
            f"Database: {info.database_name}",
            f"User: {info.user_name}",
            f"Version: {info.server_version}",
            "",
            "Connection OK. OopsQL did not execute your SQL files.",
        ]
    )


def _load_pyodbc() -> Any:
    try:
        return import_module("pyodbc")
    except ImportError as exc:
        raise SqlServerError(
            "pyodbc is not installed. Install SQL Server support with: "
            'pip install -e ".[mssql]"'
        ) from exc

