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
            line.discount = line._get_aggregated_multiple_discounts(
                [line[x] for x in line._get_multiple_discount_field_names()]
            )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("discount") and not vals.get("discount1"):
                vals["discount1"] = vals.pop("discount")
        return super().create(vals_list)

    def _get_aggregated_multiple_discounts(self, discounts):
        """
        Returns the aggregate discount corresponding to any number of discounts.
        For exemple, if discounts is [11.0, 22.0, 33.0]
        It will return 46.5114
        """
        discount_values = []
        for discount in discounts:
            discount_values.append(1 - (discount or 0.0) / 100.0)
        aggregated_discount = (
            1 - functools.reduce((lambda x, y: x * y), discount_values)
        ) * 100
        return aggregated_discount

    @api.model
    def _get_multiple_discount_field_names(self):
        return ["discount1", "discount2", "discount3"]
