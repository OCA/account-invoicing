This module helps companies that ask the customer to pay part of a sales order
before the final invoice is issued.

Instead of creating the advance somewhere else and trying to match it later, the
sales order itself shows which installments are advances and lets the user create
an advance invoice for each one.

A simple example:

1. The customer confirms an order for 1,000.00.
2. The payment term says that 30% must be paid in advance.
3. The sales order shows this 30% as an advance.
4. The user clicks **Create Advance Invoice**.
5. The customer pays that advance invoice using the normal payment flow.
6. Later, the user creates the regular invoice for the sales order.
7. At that moment, Odoo can automatically use the paid advance to reduce the
   amount still open on the regular invoice.

Only advances that come from payment term lines marked as **Advance** are handled
automatically by this module. Any other customer prepayment remains available for
manual reconciliation, as in standard Odoo.

The accounting compensation and reconciliation are still done with the logic from
`account_invoice_advance_compensation`; this module only connects that logic to
the sales order flow.
