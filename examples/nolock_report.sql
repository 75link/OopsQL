SELECT *
FROM dbo.Invoice i WITH (NOLOCK)
JOIN dbo.InvoiceItem ii WITH (NOLOCK)
  ON ii.InvoiceId = i.InvoiceId;

