# Copyright 2023 Tecnativa - Stefan Ungureanu
# Copyright 2023 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _prepare_invoice(self):
        vals = super()._prepare_invoice()
        if self.tag_ids:
            vals["crm_tag_ids"] = [(6, 0, self.tag_ids.ids)]
        return vals


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def _prepare_invoice_line(self, **optional_values):
        """Transfer CRM tags also to invoice lines, as although being a related stored,
        it's not correctly saved due to the trick/duality of invoice_line_ids/line_ids.
        """
        res = super()._prepare_invoice_line(**optional_values)
        res["crm_tag_ids"] = [(6, 0, self.order_id.tag_ids.ids)]
        return res
