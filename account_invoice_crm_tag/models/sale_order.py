# Copyright 2023 Tecnativa - Stefan Ungureanu
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _prepare_invoice(self):
        vals = super()._prepare_invoice()
        if self.tag_ids:
            vals["tag_ids"] = [(6, 0, self.tag_ids.ids)]
        return vals
