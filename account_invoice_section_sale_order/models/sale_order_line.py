# Copyright 2025 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo import models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def _prepare_invoice_line(self, **optional_values):
        values = super()._prepare_invoice_line(**optional_values)
        current_sequence = self.env.context.get("current_line_sequence")
        if current_sequence is None:
            return values
        # update the sequence of the invoice lines, add some space between lines so that
        # we can insert the sections afterwards.
        values["sequence"] = current_sequence[0]
        current_sequence[0] += 10
        return values
