To use this module, you need to:

- Activate Developer Mode.
- Go to Contacts and open a Partner (Commercial Partner) form.
- In the Invoicing tab, set `invoice_sending_method` to `email`.
- Set the "Invoice Email Subject" field.

Fallback behavior:
If the subject is empty, Odoo's default subject is used.

You can use Jinja-style placeholders based on `account.move`:
- `{{ object.name }}` → invoice number / reference
- `{{ object.partner_id.name }}` → invoice partner name
- `{{ object.invoice_date }}` → invoice date

**Example**

Enter "`Document {{ object.name }} {{ object.partner_id.name }} {{ object.invoice_date }}`"
If:
- invoice number = INV/2026/0010
- partner name = Acme Ltd
- invoice date = 2026-01-24

Then the generated subject will be:
`Document INV_2026_0010_Acme Ltd_2026-01-24`

When sending invoices via email (single or batch), the system will automatically use the partner-specific subject if set.
Otherwise, Odoo's default subject is used.
