BEGIN TRAN;

UPDATE dbo.Invoice
SET Status = 'Approved'
WHERE ClientId = 1001;

-- Verify @@ROWCOUNT before commit.
-- ROLLBACK plan: restore previous status from audit table if validation fails.
COMMIT;

