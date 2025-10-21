# Copyright 2019 Tecnativa - David Vidal
# Copyright 2019 Tecnativa - Pedro M. Baeza
# Copyright 2020 ACSONE SA/NV
# Copyright 2023 Simone Rubino - Aion Tech
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import functools

from odoo import api, fields, models


class TripleDiscountMixin(models.AbstractModel):
    _name = "triple.discount.mixin"
    _description = "Triple discount mixin"

    # core discount field is now a computed field
    # based on the 3 discounts defined below.
    # the digits limitation is removed, to make
    # the computation of the subtotal exact.
    # For exemple, if discounts are 05%, 09% and 13%
    # the main discount is 24.7885 % (and not 24.79)
    discount = fields.Float(
        string="Total discount",
        compute="_compute_discount",
        store=True,
        readonly=True,
        digits=None,
    )
    discount1 = fields.Float(string="Discount 1 (%)", digits="Discount")

    discount2 = fields.Float(string="Discount 2 (%)", digits="Discount")

    discount3 = fields.Float(string="Discount 3 (%)", digits="Discount")

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

    def _get_lines_to_compute_discount(self):
        return self

    @api.depends(lambda self: self._get_multiple_discount_field_names())
    def _compute_discount(self):
        res = True
        if hasattr(super(), "_compute_discount"):
            res = super()._compute_discount()
        for line in self._get_lines_to_compute_discount():
            line.discount = line._get_aggregated_multiple_discounts(
                [line[x] for x in line._get_multiple_discount_field_names()]
            )
        return res

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

    @api.model
    def _should_copy_discount_to_discount1(self, vals):
        """
        Primarily used to not break the functionality of other modules that write to
        the discount field that don't know/care of this modules existence.
        """
        return (
            "discount" in vals
            and "discount1" not in vals
            and "discount2" not in vals
            and "discount3" not in vals
        )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if self._should_copy_discount_to_discount1(vals):
                vals["discount1"] = vals.pop("discount")
        return super().create(vals_list)

    def write(self, vals):
        discount_fields = self._get_multiple_discount_field_names()
        if self._should_copy_discount_to_discount1(vals):
            vals["discount1"] = vals.pop("discount")
            vals.update({field: 0 for field in discount_fields[1:]})
        return super().write(vals)
