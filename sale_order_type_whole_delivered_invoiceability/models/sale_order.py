# Copyright 2024 Tecnativa - Pilar Vargas
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.depends("type_id")
    def _compute_whole_delivered_invoiceability(self):
        res = super()._compute_whole_delivered_invoiceability()
        for record in self:
            if record.type_id.whole_delivered_invoiceability:
                record.whole_delivered_invoiceability = True
        return res
