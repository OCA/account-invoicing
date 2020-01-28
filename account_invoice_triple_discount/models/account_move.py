# Copyright 2017 Tecnativa - David Vidal
# Copyright 2017 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    discount = fields.Float(
        compute="_compute_triple_discount", store=True, readonly=False
    )
    discount1 = fields.Float("Discount 1 (%)", digits="Discount")
    discount2 = fields.Float("Discount 2 (%)", digits="Discount")
    discount3 = fields.Float("Discount 3 (%)", digits="Discount")

    @api.depends("discount1", "discount2", "discount3")
    def _compute_triple_discount(self):
        for rec in self:
            d1 = 1 - (rec.discount1 or 0.0) / 100.0
            d2 = 1 - (rec.discount2 or 0.0) / 100.0
            d3 = 1 - (rec.discount3 or 0.0) / 100.0
            rec.discount = (1 - (d1 * d2 * d3)) * 100
