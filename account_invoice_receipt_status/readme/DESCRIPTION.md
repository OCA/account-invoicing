This module extends vendor bills to expose the reception status information
coming from related purchase order lines.

Specifically, it:

- Adds a field `line_receipt_status` on invoice lines.
- When the invoice line is linked to a purchase order line, the field reflects
  the reception status of the PO line (as computed by upstream modules, e.g.
  `purchase_line_receipt_status`).
- The value is readonly: it is an informational field for invoice control.

This module does **not** change quantities nor reception logic, it only
propagates the status from the purchase side onto the invoice side. It is
complementary to the module `account_invoice_purchase_qty_to_invoice`, which
allows displaying the quantity to invoice on the purchase order line alongside
the quantity already invoiced.

This improves risk control and decision making when validating vendor bills,
as the user does not need to navigate back to the related purchase orders or
stock pickings to understand the reception context.
