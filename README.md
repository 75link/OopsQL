# OopsQL

Find out what your query can mess up before you run it.

OopsQL is a lightweight T-SQL blast-radius analyzer for SQL Server. It helps developers, analysts, DBAs, ERP admins, and data architects detect risky SQL scripts before execution.

This tool does not execute SQL. It performs static analysis only.

## Overview

OopsQL reads SQL files and gives you a risk report before anyone runs the script.

It checks for:

- destructive changes like `DROP`, `TRUNCATE`, and risky `ALTER`
- `UPDATE` and `DELETE` statements without a `WHERE` clause
- missing `BEGIN TRAN` around data-changing statements
- protected tables like invoices, payments, clients, and inventory
- missing rollback notes in risky scripts
- reporting issues like `SELECT *`, `NOLOCK`, and one-to-many joins

The output is built for quick review:

- overall risk
- finding count
- rule id
- severity
- line number
- SQL excerpt
- suggestion

## What It Does

OopsQL scans `.sql` files and reports production-safety risks such as unsafe updates, deletes without filters, destructive schema changes, protected business tables, missing transactions, missing rollback guidance, and reporting queries that may duplicate totals through one-to-many joins.

It is not just a SQL linter. The focus is blast radius: touched tables, data integrity, affected-row risk, protected domains, and safer execution habits.

## Why It Exists

Many production incidents start as ordinary SQL scripts: a missing `WHERE`, an unreviewed `DROP`, a report join that doubles revenue, or a data fix with no rollback plan. OopsQL gives teams a fast local check before those scripts reach production.

## Installation

From a local checkout:

```bash
pip install -e ".[dev]"
```

## Usage

```bash
oopsql scan path/to/file.sql
oopsql scan path/to/folder
oopsql scan path/to/file.sql --format text
oopsql scan path/to/file.sql --format json
oopsql scan path/to/file.sql --format markdown
oopsql scan path/to/file.sql --min-severity HIGH
oopsql scan path/to/file.sql --fail-on CRITICAL
oopsql scan path/to/file.sql --config path/to/oopsql.yml
oopsql init-config
```

`oopsql init-config` writes an `oopsql.yml` file in the current directory.

By default, `oopsql scan` exits with code `1` when it finds any risk. Use `--fail-on HIGH`, `--fail-on CRITICAL`, or `--fail-on NONE` to control that behavior in CI.

## Website

Open `docs/index.html` in a browser to see the static project page.

## Example Output

```text
OopsQL Risk Report
File: examples/dangerous_update.sql

Overall Risk: CRITICAL
Findings: 4

[CRITICAL] OOPS001 - UPDATE without WHERE
Line: 1
Message: UPDATE statement detected without a WHERE clause.
Suggestion: Add a WHERE clause, run a SELECT preview first, and wrap the change in a transaction.
```

## Configuration

```yaml
protected_tables:
  - invoice
  - invoiceitem
  - payment
  - glentry
  - inventory
  - client
  - purchaseorder

risky_keywords:
  - production
  - finance
  - revenue
  - accounting

require_transaction_for:
  - UPDATE
  - DELETE
  - MERGE
  - INSERT
  - ALTER
  - DROP
  - TRUNCATE
```

## Rules

| Rule | Severity | Description |
| --- | --- | --- |
| OOPS001 | CRITICAL | UPDATE without WHERE |
| OOPS002 | CRITICAL | DELETE without WHERE |
| OOPS003 | CRITICAL | TRUNCATE TABLE detected |
| OOPS004 | CRITICAL | DROP statement detected |
| OOPS005 | HIGH | ALTER statement detected |
| OOPS006 | HIGH | MERGE statement detected |
| OOPS007 | HIGH | Data-changing statement without explicit transaction |
| OOPS008 | MEDIUM | SELECT * detected |
| OOPS009 | MEDIUM | NOLOCK detected |
| OOPS010 | HIGH | Protected table touched |
| OOPS011 | MEDIUM | Missing rollback comment or section |
| OOPS012 | MEDIUM | Possible one-to-many reporting join risk |

## Suggested Safer Scripts

For `UPDATE` and `DELETE` statements with a `WHERE` clause, OopsQL can include a preview template that wraps the change in a transaction and shows the rows before modification.

## Roadmap

- Improve T-SQL parsing with richer statement and table extraction.
- Estimate affected rows through optional database metadata integrations.
- Add SARIF output for code scanning workflows.
- Support rule suppression comments.
- Add CI examples for pull requests.

## Contributing

Issues and pull requests are welcome. Please include tests for rule behavior changes and keep in mind that OopsQL must never execute user SQL.
