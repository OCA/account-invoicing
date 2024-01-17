# Copyright 2023 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class SaleOrder(models.Model):
    _inherit = "sale.order.line"

    def _prepare_invoice_line(self, **optional_values):
        """If invoicing by quantity percentage, modify quantities."""
        res = super()._prepare_invoice_line(**optional_values)
        if self.env.context.get("qty_percentage"):
            res["quantity"] *= self.env.context["qty_percentage"]
        return res
