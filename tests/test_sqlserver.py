import sys
from types import SimpleNamespace

import pytest

from oopsql.sqlserver import SqlServerError, format_connection_info
from oopsql.sqlserver import test_connection as run_connection_test


class FakeCursor:
    def execute(self, sql):
        self.sql = sql
        return self

    def fetchone(self):
        return SimpleNamespace(
            server_name="DEV-SQL",
            database_name="master",
            user_name="dbo",
            server_version="16.0.1000.6",
        )


class FakeConnection:
    def __init__(self):
        self.closed = False

    def cursor(self):
        return FakeCursor()

    def close(self):
        self.closed = True


def test_sqlserver_connection_uses_pyodbc(monkeypatch):
    calls = {}

    def connect(connection_string, timeout):
        calls["connection_string"] = connection_string
        calls["timeout"] = timeout
        return FakeConnection()

    monkeypatch.setitem(sys.modules, "pyodbc", SimpleNamespace(connect=connect))

    info = run_connection_test("Driver={ODBC Driver 18 for SQL Server};Server=.;", timeout=3)

    assert calls["timeout"] == 3
    assert info.server_name == "DEV-SQL"
    assert info.database_name == "master"


def test_connection_info_format():
    output = format_connection_info(
        SimpleNamespace(
            server_name="DEV-SQL",
            database_name="master",
            user_name="dbo",
            server_version="16.0.1000.6",
        )
    )

    assert "Connection OK" in output
    assert "Server: DEV-SQL" in output


def test_missing_pyodbc_message(monkeypatch):
    import oopsql.sqlserver as sqlserver

    def missing_module(name):
        raise ImportError(name)

    monkeypatch.setattr(sqlserver, "import_module", missing_module)

    with pytest.raises(SqlServerError, match="pip install"):
        run_connection_test("Driver={ODBC Driver 18 for SQL Server};Server=.;")
