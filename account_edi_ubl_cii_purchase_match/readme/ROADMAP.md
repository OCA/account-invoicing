This module implements custom purchase order line matching and replaces
the standard behavior of linking vendor bills to purchase orders via UBL.

Before migrating to future versions, it is recommended to verify whether:
- Odoo natively supports precise line-level matching,
- supplier product names and UBL descriptions are matched out of the box,
- and the original UBL lines are preserved.

If the standard behavior evolves to fully cover this business requirement,
this module may become unnecessary.
