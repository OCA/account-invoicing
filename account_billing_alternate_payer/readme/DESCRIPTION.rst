This module makes the billing document group the invoices by the partner that
actually pays them.

``account_billing`` collects the open invoices whose partner is the billing
partner. ``account_invoice_alternate_payer`` allows issuing an invoice to one
partner while the receivable belongs to another one, the alternate payer.

With both modules installed, a billing document for a payer lists every invoice
that partner has to pay, even when each invoice was issued to a different
customer, and each line shows the partner the invoice was issued to.
