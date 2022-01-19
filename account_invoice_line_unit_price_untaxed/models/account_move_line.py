# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class AccountMoveLine(models.Model):

    _inherit = "account.move.line"

    price_unit_untaxed = fields.Float(
        compute="_compute_price_unit_untaxed",
        string="Price without Taxes",
        digits="Product Price",
        store=True,
    )

    @api.depends("product_id", "price_unit", "tax_ids")
    def _compute_price_unit_untaxed(self):
        for line in self:
            tot = line.tax_ids.compute_all(
                line.price_unit, quantity=1, product=line.product_id
            )
            line.price_unit_untaxed = tot["total_excluded"]
