When a vendor (or customer) sends an email to a billing journal's alias
(for example ``vendor-bills@yourcompany.odoo.com``) without attaching the
invoice PDF/XML, Odoo does not generate any record by default and that
communication is lost.

This module intercepts the reception of those emails (``account.move``'s
``message_new``) and:

* If the email carries a valid attachment (PDF/XML): the normal Odoo flow
  is followed (draft invoice/bill creation, digitization, etc.)
* If the email does NOT carry a valid attachment:

  * A draft ``account.move`` is created anyway, flagged as "Received
    without attachment".
  * The sending contact (vendor/customer) is looked up from the sender
    email (exact match, or same domain among already loaded contacts).
  * The original sender email is stored.
  * A "To Do" activity is scheduled so a responsible user reviews the
    case and requests the document to be resent.

It also adds a **Failed Invoices** menu listing every pending case, and an
optional cron that flags invoices whose OCR/digitization process ended in
error (only active when an invoice digitization module, such as the
Enterprise ``account_invoice_extract``, is installed).