# Copyright 2026 Akretion
# @author Guillaume MASSON <guillaume.masson@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def _get_warehouse(self):
        """Return the warehouse of the sale order line.

        Can be overridden by a glue module if warehouse_id is defined
        at the sale.order.line level.
        """
        return self.order_id.warehouse_id
