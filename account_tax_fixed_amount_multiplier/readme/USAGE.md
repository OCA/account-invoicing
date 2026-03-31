**Product Quantity** mode is useful for per-unit taxes where the product may
be sold in different units of measure.

For example, if a product is defined in *Units* and has a per-unit tax of
5.00, selling 1 *Dozen* will compute the tax as:

    1 dozen = 12 units → tax = 12 × 5.00 = 60.00

This also works with nested UoM hierarchies. For example, selling 1 *Box of
10 Dozens* will compute:

    1 box = 10 dozens = 120 units → tax = 120 × 5.00 = 600.00

**Product Weight** mode is useful for weight-based fees. For example, with
a levy of 3.00 per kilogram and a product weighing 2.5 kg:

    10 units × 2.5 kg/unit × 3.00/kg = 75.00

If `account_tax_fixed_amount_currency` is also installed, configure the fixed
tax currency on the tax as usual. The multiplier changes the quantity used by
the fixed tax computation, and the resulting amount is then converted by the
currency module.
