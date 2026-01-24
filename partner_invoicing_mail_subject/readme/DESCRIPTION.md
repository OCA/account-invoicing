This module extends the functionality of Invoice mailing to allow partners to have
individual invoice email subjects. It ensures that the partner-specific subject is used when sending invoices,
both for single and batch invoice emails.

- Adds a new field invoice_email_subject on partners (commercial partners) to define a custom subject line
for invoice emails.
- Automatically uses the partner-specific subject when sending invoices via email.
- If no individual subject is set, the standard email template subject is used.
- Works for both single invoice and batch invoice sending.
