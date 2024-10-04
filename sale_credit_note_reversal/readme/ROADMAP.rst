An integration with sale_line_refund_to_invoice_qty module will be very useful.
The reverted credit note does not add quantity to the qty_invoiced. The credit
note does also not update the qty_to_invoice in the normal case, so at least
this reversal is consistent.
