# Copyright 2026 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.tools import float_compare


class AccountMoveLine(models.Model):
    _inherit = ["account.move.line", "product.secondary.unit.mixin"]
    _name = "account.move.line"
    _secondary_unit_fields = {
        "qty_field": "quantity",
        "uom_field": "product_uom_id",
    }

    secondary_uom_price = fields.Float(
        string="Secondary Price",
        digits="Product Price",
        aggregator="avg",
        compute="_compute_secondary_uom_price",
        inverse="_inverse_secondary_uom_price",
        store=True,
    )

    @api.depends("display_type", "secondary_uom_qty", "secondary_uom_id")
    def _compute_quantity(self):
        res = super()._compute_quantity()
        self._compute_helper_target_field_qty()
        return res

    def _get_secondary_uom_price(self, price_unit):
        """Convert a price per line UoM into a price per secondary unit."""
        self.ensure_one()
        price_product_uom = self._get_uom_line()._compute_price(
            price_unit, self._get_product_uom()
        )
        return price_product_uom * self.secondary_uom_id.factor

    @api.depends(
        "price_unit",
        "product_uom_id",
        "product_id.uom_id",
        "secondary_uom_id",
        "secondary_uom_id.factor",
    )
    def _compute_secondary_uom_price(self):
        for rec in self:
            if rec.secondary_uom_id.factor:
                rec.secondary_uom_price = rec._get_secondary_uom_price(rec.price_unit)
            else:
                rec.secondary_uom_price = 0.0

    @api.onchange("secondary_uom_price")
    def _inverse_secondary_uom_price(self):
        precision = self.env["decimal.precision"].precision_get("Product Price")
        for rec in self:
            if not rec.secondary_uom_id.factor:
                continue
            # Keep the unit price when the secondary price only differs from it
            # by rounding, so that a typed unit price is not rewritten.
            if (
                rec.price_unit
                and float_compare(
                    rec.secondary_uom_price,
                    rec._get_secondary_uom_price(rec.price_unit),
                    precision_digits=precision,
                )
                == 0
            ):
                continue
            price_product_uom = rec.secondary_uom_price / rec.secondary_uom_id.factor
            rec.price_unit = rec._get_product_uom()._compute_price(
                price_product_uom, rec._get_uom_line()
            )

    @api.onchange("product_uom_id")
    def onchange_product_uom_for_secondary(self):
        self._onchange_helper_product_uom_for_secondary()
