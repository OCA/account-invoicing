To use this module, you need to:

- Activate Developer Mode.
- Go to Contacts and open a Partner (Commercial Partner) form.
- In the Invoicing tab, set `invoice_sending_method` to `email`.
- Set a custom PDF filename in `invoice_pdf_filename`.

Fallback behavior:
If the template is empty or rendering fails, Odoo's default report filename is used.

You can use Jinja-style placeholders based on `account.move`:

- `{{ object.name }}` → invoice number / reference
- `{{ object.partner_id.name }}` → invoice partner name
- `{{ object.invoice_date }}` → invoice date

**Example**

Enter:
`Document_{{ object.name }}_{{ object.partner_id.name }}_{{ object.invoice_date }}`

If:
- invoice number = INV/2026/0010
- partner name = Acme Ltd
- invoice date = 2026-01-24

Then the generated PDF filename will be:
`Document_INV_2026_0010_Acme_Ltd_2026-01-24.pdf`

When generating invoice PDFs (single or batch), the system will automatically use the partner-specific filename if set.
Otherwise, Odoo's default report filename is used.
