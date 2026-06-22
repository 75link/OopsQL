from oopsql.config import config_from_dict
from oopsql.rules import analyze_sql


CONFIG = config_from_dict(
    {
        "protected_tables": ["invoice", "payment", "client"],
        "require_transaction_for": [
            "UPDATE",
            "DELETE",
            "MERGE",
            "INSERT",
            "ALTER",
            "DROP",
            "TRUNCATE",
        ],
    }
)


def rule_ids(sql: str) -> set[str]:
    return {finding.rule_id for finding in analyze_sql(sql, CONFIG)}


def test_update_without_where():
    assert "OOPS001" in rule_ids("UPDATE dbo.Invoice SET Status = 'Paid';")


def test_delete_without_where():
    assert "OOPS002" in rule_ids("DELETE FROM dbo.Payment;")


def test_safe_update_with_where_and_transaction():
    sql = """
    BEGIN TRAN;
    UPDATE dbo.Invoice SET Status = 'Paid' WHERE InvoiceId = 1;
    -- rollback plan: set Status back to Pending.
    COMMIT;
    """
    ids = rule_ids(sql)
    assert "OOPS001" not in ids
    assert "OOPS007" not in ids
    assert "OOPS011" not in ids


def test_select_star():
    assert "OOPS008" in rule_ids("SELECT * FROM dbo.Invoice;")


def test_nolock():
    assert "OOPS009" in rule_ids("SELECT InvoiceId FROM dbo.Invoice WITH (NOLOCK);")


def test_protected_table_detection():
    assert "OOPS010" in rule_ids("UPDATE dbo.Client SET Name = 'A' WHERE ClientId = 1;")

