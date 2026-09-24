This module extends invoice PDF generation by allowing individual PDF filename templates on partners.
It ensures that partner-specific Jinja templates are used when generating invoice PDFs.

- Adds a new field invoice_pdf_filename on partners (commercial partners) to define a custom PDF filename template.
- Supports Jinja-style placeholders based on account.move, for example:
  - {{ object.name }} → invoice number / reference
  - {{ object.partner_id.name }} → invoice partner name
  - {{ object.invoice_date }} → invoice date

- Automatically generates the PDF filename using the partner-specific template if set.
- Works for both single invoice PDF generation and batch processing.
- If the template is empty or rendering fails, Odoo’s default report filename is used.
