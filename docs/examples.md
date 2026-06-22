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

