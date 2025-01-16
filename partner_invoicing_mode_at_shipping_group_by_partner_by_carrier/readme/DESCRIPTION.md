As the `stock_picking_group_by_partner_by_carrier` module does not use the `sale_id` field
on the `stock.picking` module, there is no more trigger to create the invoice at
picking validation.

This module handles that use case restablishing the trigger.
