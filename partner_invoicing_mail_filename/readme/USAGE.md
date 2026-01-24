To use this module, you need to:

- Go to Contacts and open a Partner (Commercial Partner) form.
- In the Invoicing tab, under the Customer Invoices section, set a custom PDF filename to invoice_pdf_filename.
  - You can use the following placeholders:
    - {invoice_number} → the invoice reference
    - {partner_name} → the invoice partner name
    - {invoice_date} → the invoice date
    - {default} → the standard report filename (core Odoo filename, e.g., from _get_report_base_filename())
  - Example:
    - Enter "`Document_{invoice_number}_{partner_name}_{invoice_date}_{default}`"
    - If:
      - invoice number = INV/2026/0010
      - partner name = Acme Ltd
      - default report filename = INV/2026/0010 (from _get_report_base_filename())
    - Then the generated PDF filename will be:
      `Document_INV_2026_0010_Acme_Ltd_2026-01-24_INV_2026_0010.pdf`
    - Save the partner.

When generating invoice PDFs (single or batch), the system will automatically use the partner-specific filename if set.
If no custom filename is defined, the standard report filename from Odoo will be used.
