In Odoo when account user create refund directly (not from an invoice),
sales payment terms (those used for invoicing) are used.

This module add new refund payment term field on partner
to manage payment terms for refunds different to those used for invoicing.

This avoid to wrongly split generated account move lines with different due
dates for refunds and properly configure payment terms messages on refund
document (PDF).
