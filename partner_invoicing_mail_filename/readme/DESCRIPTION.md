This module extends the functionality of invoice PDF generation to allow partners to have individual PDF filenames.
It ensures that the partner-specific filename template is used when generating invoice PDFs.

- Adds a new field invoice_pdf_filename on partners (commercial partners) to define a custom PDF filename template.
- Supports dynamic placeholders in the filename:
  - {invoice_number} → the invoice reference
  - {partner_name} → the partner name
  - {invoice_date} → the invoice date
  - {default} → the standard report filename (core Odoo filename, e.g., from _get_report_base_filename())
- Automatically generates the PDF filename using the partner-specific template if set.
- Works for both single invoice PDF generation and batch processing.
