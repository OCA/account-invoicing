# Copyright 2026 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


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

    @api.depends("price_unit", "secondary_uom_id", "secondary_uom_id.factor")
    def _compute_secondary_uom_price(self):
        for rec in self:
            if rec.secondary_uom_id.factor:
                rec.secondary_uom_price = rec.price_unit * rec.secondary_uom_id.factor
            else:
                rec.secondary_uom_price = 0.0

    @api.onchange("secondary_uom_price")
    def _inverse_secondary_uom_price(self):
        for rec in self:
            if rec.secondary_uom_id.factor:
                rec.price_unit = rec.secondary_uom_price / rec.secondary_uom_id.factor

    @api.onchange("product_uom_id")
    def onchange_product_uom_for_secondary(self):
        self._onchange_helper_product_uom_for_secondary()
