BEGIN TRAN;

DELETE FROM dbo.Client
WHERE ClientId = 42;

-- ROLLBACK plan: restore deleted row from latest backup or audit export.
-- ROLLBACK;

