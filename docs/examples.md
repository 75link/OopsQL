# Examples

Scan a single file:

```bash
oopsql scan examples/dangerous_update.sql
```

Scan a folder:

```bash
oopsql scan examples
```

Return JSON:

```bash
oopsql scan examples/dangerous_update.sql --format json
```

Return Markdown:

```bash
oopsql scan examples --format markdown
```

Only show high and critical findings:

```bash
oopsql scan examples --min-severity HIGH
```

Only fail CI on critical findings:

```bash
oopsql scan examples --fail-on CRITICAL
```

Use a specific config file:

```bash
oopsql scan examples --config ./oopsql.yml
```

Create a config file:

```bash
oopsql init-config
```

## Safe Data Fix Pattern

```sql
BEGIN TRAN;

SELECT *
FROM dbo.Invoice
WHERE ClientId = 1001;

UPDATE dbo.Invoice
SET Status = 'Approved'
WHERE ClientId = 1001;

-- Check @@ROWCOUNT before committing.
-- COMMIT;
-- ROLLBACK;
```
