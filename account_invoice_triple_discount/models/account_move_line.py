# Copyright 2020 ACSONE SA/NV
# Copyright 2023 Simone Rubino - Aion Tech
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import functools

from odoo import api, fields, models


class AccountMoveLine(models.Model):

    _inherit = "account.move.line"

    discount = fields.Float(
        string="Total discount",
        compute="_compute_discount",
        store=True,
        readonly=True,
    )
    discount1 = fields.Float(
        string="Discount 1 (%)",
        digits="Discount",
    )
    discount2 = fields.Float(
        string="Discount 2 (%)",
        digits="Discount",
    )
    discount3 = fields.Float(
        string="Discount 3 (%)",
        digits="Discount",
    )

    @api.depends("discount1", "discount2", "discount3")
    def _compute_discount(self):
        for line in self:
            line.discount = line._get_aggregated_discount_from_values(
                {
                    fname: line[fname]
                    for fname in line._get_multiple_discount_field_names()
                }
            )

    def _get_aggregated_discount_from_values(self, values):
        discount_fnames = self._get_multiple_discount_field_names()
        discounts = []
        for discount_fname in discount_fnames:
            discounts.append(values.get(discount_fname) or 0.0)
        return self._get_aggregated_multiple_discounts(discounts)

    def _get_aggregated_multiple_discounts(self, discounts):
        discount_values = []
        for discount in discounts:
            discount_values.append(1 - (discount or 0.0) / 100.0)
        aggregated_discount = (
            1 - functools.reduce((lambda x, y: x * y), discount_values)
        ) * 100
        return aggregated_discount

    def _get_multiple_discount_field_names(self):
        return ["discount1", "discount2", "discount3"]
