# OopsQL SSMS Guard

Goal: show an OopsQL warning popup inside SQL Server Management Studio before a risky query runs.

SSMS is the editor. SQL Server is the database. To warn before execution, OopsQL needs an SSMS extension that hooks the Execute command, reads the current query text, sends it to OopsQL, and shows a confirmation dialog when risk is found.

## Flow

1. User presses Execute in SSMS.
2. SSMS extension reads the active query window text.
3. Extension calls:

```powershell
oopsql scan-stdin --file ssms-query.sql --format json --fail-on HIGH
```

4. Extension parses the JSON.
5. If risk is `HIGH` or `CRITICAL`, show a popup.
6. User chooses Cancel or Run anyway.
7. If user cancels, the extension stops execution.

## Popup text

```text
OopsQL found risky SQL before execution.

Overall Risk: CRITICAL
Findings: 4

- OOPS001 UPDATE without WHERE
- OOPS010 Protected table touched: invoice
- OOPS007 Missing transaction

Cancel or run anyway?
```

## Command bridge

The Python CLI now supports stdin so an SSMS extension can scan unsaved query text:

```powershell
Get-Content .\query.sql | oopsql scan-stdin --file ssms-query.sql --format json
```

## Windows build

Build a standalone `oopsql.exe` for the extension to call:

```powershell
pip install -e ".[exe]"
sh scripts/build-exe.sh
```

The executable is created at `dist/oopsql`.

## Important

This cannot be done from Python alone. A real pre-execution popup inside SSMS needs a Windows SSMS extension because the query text and Execute command live inside SSMS.

