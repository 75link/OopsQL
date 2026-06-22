# Rules

OopsQL rules focus on blast-radius risk rather than formatting style.

| Rule | Severity | Description | Default suggestion |
| --- | --- | --- | --- |
| OOPS001 | CRITICAL | UPDATE without WHERE | Add a WHERE clause, preview rows first, and use a transaction. |
| OOPS002 | CRITICAL | DELETE without WHERE | Add a WHERE clause, preview rows first, and use a transaction. |
| OOPS003 | CRITICAL | TRUNCATE TABLE detected | Require review and a recovery plan. |
| OOPS004 | CRITICAL | DROP statement detected | Require backup, review, and rollback steps. |
| OOPS005 | HIGH | ALTER statement detected | Review schema impact and deployment order. |
| OOPS006 | HIGH | MERGE statement detected | Validate match conditions and duplicate-match behavior. |
| OOPS007 | HIGH | Data-changing statement without explicit transaction | Use BEGIN TRAN, verify @@ROWCOUNT, then COMMIT or ROLLBACK. |
| OOPS008 | MEDIUM | SELECT * detected | Select explicit columns. |
| OOPS009 | MEDIUM | NOLOCK detected | Avoid dirty reads unless the risk is accepted. |
| OOPS010 | HIGH | Protected table touched | Require review before modifying protected business data. |
| OOPS011 | MEDIUM | Missing rollback comment or section | Add a rollback plan before production execution. |
| OOPS012 | MEDIUM | Possible one-to-many reporting join risk | Check join grain and pre-aggregate child tables. |

## Notes

This MVP uses static statement-level heuristics. It does not connect to SQL Server and does not execute SQL.

