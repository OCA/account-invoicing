When an invoice PDF is generated via **Send & Print**, Odoo caches it as an
``ir.attachment`` linked to the ``invoice_pdf_report_file`` field on the
invoice. Any subsequent print or send operation will reuse that cached PDF
instead of generating a new one.

This becomes a problem when a payment is registered *after* the initial PDF
was generated: the cached PDF still shows the old payment status (e.g.
"Amount Due: $500") even though the payment has been fully reconciled in the
system.

This module automatically deletes the cached invoice PDF attachment whenever
a payment is registered through the **Register Payment** wizard, so that the
next time the invoice is printed or sent the PDF is regenerated with accurate,
up-to-date payment information.
