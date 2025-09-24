# Copyright 2025 Ethan Hildick
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models
from odoo.tools.float_utils import float_is_zero


class TripleDiscountMixin(models.AbstractModel):
    _inherit = "triple.discount.mixin"

    def _should_copy_discount_to_discount1(self, vals):
        res = super()._should_copy_discount_to_discount1(vals)
        currency = (
            self.env["res.currency"].browse(vals.get("currency_id"))
            or self.env.company.currency_id
        )
        return res and not (
            "discount_fixed" in vals
            and not float_is_zero(
                vals.get("discount_fixed"),
                precision_rounding=currency.rounding,
            )
        )
