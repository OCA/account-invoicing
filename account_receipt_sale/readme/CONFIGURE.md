- On a partner, tick "Use Receipts" to flag new sale orders as receipts
  by default.
- On the "Create Invoices" wizard, tick "Receipts" to generate receipts
  (move_type `out_receipt`) instead of regular invoices. The wizard
  checkbox is preselected from the sale order's flag and is
  authoritative for the run.

Note: when installed on a database that already contains receipts
linked to sale order lines, the module performs a one-time recompute
of `qty_invoiced` and `untaxed_amount_invoiced` on the affected lines.
Installation time scales with the number of pre-existing receipts.
