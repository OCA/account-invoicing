This module adds a multiplier option to fixed-amount taxes, controlling how
the line quantity is used in the tax computation.

By default, Odoo computes fixed taxes as `line quantity × amount`. This
module allows choosing between four multiplier modes:

- **No Multiplier**: the amount is applied once per line, regardless of
  quantity. Useful for per-document fees (e.g., stamp duties).
- **Quantity (default)**: standard behavior, equivalent to
  `line quantity × amount`.
- **Product Quantity**: the line quantity is first converted to the
  product's unit of measure before multiplying. This is useful when the tax
  is defined per unit of the product, but the line may use a different UoM
  (e.g., selling in dozens while the product is defined in units).
- **Product Weight**: multiplied by the total weight of the products on the
  line (product quantity × product weight). Useful for weight-based fees
  such as environmental levies.

This module is compatible with `account_tax_fixed_amount_currency` without
depending on it. When both modules are installed, the selected multiplier
changes the fixed-tax quantity first, and the currency module can then convert
the resulting fixed amount to the document currency through the normal tax
computation chain.
