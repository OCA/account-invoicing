# Copyright 2026 Akretion
# @author Guillaume MASSON <guillaume.masson@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    def _get_warehouse(self):
        """Return the warehouse of the purchase order line.

        Can be overridden by a glue module if warehouse_id is defined
        at the purchase.order.line level.
        The warehouse is retrieved from the picking type of the purchase order,
        which represents the destination warehouse.
        """
        self.ensure_one()
        return self.order_id.picking_type_id.warehouse_id
