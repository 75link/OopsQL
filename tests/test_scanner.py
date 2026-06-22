from pathlib import Path

from oopsql.config import config_from_dict
from oopsql.scanner import scan_file, scan_path


CONFIG = config_from_dict(
    {
        "protected_tables": ["invoice"],
        "require_transaction_for": ["UPDATE", "DELETE"],
    }
)


def test_scan_file_detects_update_without_where(tmp_path: Path):
    sql_file = tmp_path / "danger.sql"
    sql_file.write_text("UPDATE dbo.Invoice SET Status = 'Paid';", encoding="utf-8")

    report = scan_file(sql_file, CONFIG)

    assert report.overall_risk == "CRITICAL"
    assert any(finding.rule_id == "OOPS001" for finding in report.findings)


def test_scan_folder_finds_sql_files(tmp_path: Path):
    (tmp_path / "a.sql").write_text("SELECT * FROM dbo.Invoice;", encoding="utf-8")
    (tmp_path / "notes.txt").write_text("SELECT * FROM dbo.Invoice;", encoding="utf-8")

    reports = scan_path(tmp_path, CONFIG)

    assert len(reports) == 1
    assert reports[0].file.endswith("a.sql")

