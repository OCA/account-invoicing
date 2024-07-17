* The selection of pickings for the section name relies on the last invoice
  that was created and is linked to the sale order line. In such case, there's
  no guarantee the selection is correct if the quantity is reduced on prior
  invoice lines.
* Moreover, as Odoo considers the draft invoices for the computation of
  `qty_invoiced` on sales order line, we couldn't base the selection of the last
  invoice on another field than the `create_date` although it would have been
  cleaner to rely on a `date` field, but this one is only set on the posting.
  Finally, defining another field for the generation of invoices wouldn't have
  helped solve these issues.
