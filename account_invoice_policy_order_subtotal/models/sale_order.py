# Copyright 2022 Camptocamp SA <telmo.santos@camptocamp.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo import models
from odoo.tools import float_compare


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _get_invoiceable_lines(self, final=False):
        precision = self.env["decimal.precision"].precision_get("Product Price")
        lines = super()._get_invoiceable_lines(final=final)
        subtot_policy_lns = self.order_line._get_policy_order_subtotal_lines()
        # Filter subtot_policy_lns from invoiveable lines got in super call
        lines -= subtot_policy_lns
        # Add subtot_policy_lns with amount to invoice > 0
        lines |= subtot_policy_lns.filtered(
            lambda line: float_compare(
                abs(line.price_subtotal),
                abs(line.amount_invoiced),
                precision_digits=precision,
            )
            > 0
        )
        return lines
