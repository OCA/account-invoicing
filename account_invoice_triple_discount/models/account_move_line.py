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

    def _fix_triple_discount_values(self, values):
        res = values
        if "discount" in values and "discount1" not in values:
            res = values.copy()
            res["discount1"] = res.pop("discount")
        return res

    # In case sale is installed but not sale_triple_discount, Odoo
    #  will propagate sale.order.line.discount into account.move.line.discount
    #  but account.move.line.discount1 will not be set properly
    # Override create/write and only in case discount is set but not
    #  discount1, move its value to discount1
    @api.model_create_multi
    def create(self, vals_list):
        for i, vals in enumerate(vals_list):
            new_vals = self._fix_triple_discount_values(vals)
            if new_vals:
                vals_list[i] = new_vals
        return super().create(vals_list)

    def write(self, vals):
        vals = self._fix_triple_discount_values(vals)
        return super().write(vals)
