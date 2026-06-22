import json

from oopsql.formatter import format_reports
from oopsql.models import Finding, RiskReport


def test_json_output_structure():
    report = RiskReport(
        file="danger.sql",
        findings=[
            Finding(
                rule_id="OOPS001",
                severity="CRITICAL",
                line=1,
                message="UPDATE statement detected without a WHERE clause.",
                suggestion="Add a WHERE clause.",
                excerpt="UPDATE dbo.Invoice SET Status = 'Paid';",
            )
        ],
    )

    payload = json.loads(format_reports([report], "json"))

    assert payload["file"] == "danger.sql"
    assert payload["overall_risk"] == "CRITICAL"
    assert payload["findings_count"] == 1
    assert payload["findings"][0]["rule_id"] == "OOPS001"


def test_text_output_includes_core_report_fields():
    report = RiskReport(file="safe.sql", findings=[])

    output = format_reports([report], "text")

    assert "OopsQL Risk Report" in output
    assert "Overall Risk: LOW" in output
    assert "Findings: 0" in output

