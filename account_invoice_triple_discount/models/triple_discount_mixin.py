# Copyright 2019 Tecnativa - David Vidal
# Copyright 2019 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import functools

from odoo import api, fields, models


class TripleDiscount(models.AbstractModel):
    # TODO: To be moved to account_invoice_triple_discount
    _name = "triple.discount.mixin"
    _description = "Triple discount mixin"

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

    _sql_constraints = [
        (
            "discount1_limit",
            "CHECK (discount1 <= 100.0)",
            "Discount 1 must be lower than 100%.",
        ),
        (
            "discount2_limit",
            "CHECK (discount2 <= 100.0)",
            "Discount 2 must be lower than 100%.",
        ),
        (
            "discount3_limit",
            "CHECK (discount3 <= 100.0)",
            "Discount 3 must be lower than 100%.",
        ),
    ]

    @api.depends(lambda self: self._get_multiple_discount_field_names())
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

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("discount") and not any(
                vals.get(field) for field in self._get_multiple_discount_field_names()
            ):
                vals["discount1"] = vals.pop("discount")
        return super().create(vals_list)

    def write(self, vals):
        discount_fields = self._get_multiple_discount_field_names()
        if "discount" in vals:
            vals["discount1"] = vals.pop("discount")
            vals.update({field: 0 for field in discount_fields[1:]})
        return super().write(vals)
