from pathlib import Path
from io import StringIO

from oopsql.cli import main


def test_cli_min_severity_filters_output(tmp_path: Path, capsys):
    sql_file = tmp_path / "report.sql"
    sql_file.write_text("SELECT * FROM dbo.ReportCache WITH (NOLOCK);", encoding="utf-8")

    exit_code = main(["scan", str(sql_file), "--min-severity", "HIGH"])
    output = capsys.readouterr().out

    assert exit_code == 0
    assert "Findings: 0" in output
    assert "OOPS008" not in output
    assert "OOPS009" not in output


def test_cli_fail_on_none_returns_zero_for_findings(tmp_path: Path, capsys):
    sql_file = tmp_path / "danger.sql"
    sql_file.write_text("DELETE FROM dbo.Invoice;", encoding="utf-8")

    exit_code = main(["scan", str(sql_file), "--fail-on", "NONE"])

    assert exit_code == 0


def test_cli_custom_config_path(tmp_path: Path, capsys):
    sql_file = tmp_path / "change.sql"
    config_file = tmp_path / "custom.yml"
    sql_file.write_text(
        "BEGIN TRAN; UPDATE dbo.SpecialLedger SET Posted = 1 WHERE Id = 4; -- rollback",
        encoding="utf-8",
    )
    config_file.write_text(
        """
protected_tables:
  - specialledger
require_transaction_for:
  - UPDATE
""",
        encoding="utf-8",
    )

    exit_code = main(["scan", str(sql_file), "--config", str(config_file)])
    output = capsys.readouterr().out

    assert exit_code == 1
    assert "protected table: specialledger" in output


def test_cli_scan_stdin(monkeypatch, capsys):
    monkeypatch.setattr("sys.stdin", StringIO("UPDATE dbo.Invoice SET Status = 'Paid';"))

    exit_code = main(["scan-stdin", "--file", "ssms-query.sql", "--format", "text"])
    output = capsys.readouterr().out

    assert exit_code == 1
    assert "File: ssms-query.sql" in output
    assert "OOPS001" in output
