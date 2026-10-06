This module extends the functionality of invoice mailing by allowing custom invoice email subjects on partners
using Odoo QWeb templates. It enables dynamic subject lines based on invoice data using standard Odoo mail rendering
(object-based fields).

- Adds a new field `invoice_email_subject` on commercial partners to define a custom invoice email subject template.
- Supports Odoo QWeb expressions such as `{{ object.name }}`, `{{ object.invoice_date }}`, etc.
- Automatically renders the subject using the invoice (`account.move`) as context.
- If no custom subject is defined, the standard Odoo email subject is used.
- Works for both single invoice and batch invoice sending.
- Invalid template fields are validated against the `account.move` model to prevent configuration errors.
