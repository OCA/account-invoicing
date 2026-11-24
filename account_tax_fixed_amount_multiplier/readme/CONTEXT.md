In standard Odoo, fixed-amount taxes are multiplied by the line quantity
as entered on the document. This means that if a product is sold in dozens,
the tax is multiplied by 1 (the line quantity) instead of 12 (the actual
number of units).

This can be problematic for taxes or fees that are defined per unit of
product, such as:

- **Per-unit recycling fees**: a fixed fee per unit sold, regardless of
  the unit of measure used on the sales line.
- **Per-kilogram levies**: a fee based on the total weight of the products
  sold (e.g., environmental taxes on volatile organic compounds).
- **Per-document stamps or duties**: a fixed fee applied once per line,
  regardless of the quantity.

This module addresses these use cases by allowing to control how the
quantity is interpreted in the tax computation.
