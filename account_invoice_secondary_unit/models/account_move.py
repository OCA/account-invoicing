# Copyright 2020 Jarsa
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl)

from odoo import api, fields, models
from odoo.tools.float_utils import float_compare, float_round


class AccountMove(models.Model):
    _inherit = "account.move.line"

    secondary_uom_qty = fields.Float(
        string="Secondary Qty", digits="Product Unit of Measure"
    )
    secondary_uom_id = fields.Many2one(
        comodel_name="product.secondary.unit",
        string="Secondary UoM",
        ondelete="restrict",
    )

    @api.onchange("secondary_uom_id", "secondary_uom_qty")
    def onchange_secondary_uom(self):
        if not self.secondary_uom_id:
            return
        factor = self.secondary_uom_id.factor * self.product_uom_id.factor
        qty = float_round(
            self.secondary_uom_qty * factor,
            precision_rounding=self.product_uom_id.rounding,
        )
        if (
            float_compare(
                self.quantity, qty, precision_rounding=self.product_uom_id.rounding
            )
            != 0
        ):
            self.quantity = qty

    @api.onchange("quantity")
    def onchange_secondary_unit_quantity(self):
        if not self.secondary_uom_id:
            return
        factor = self.secondary_uom_id.factor * self.product_uom_id.factor
        qty = float_round(
            self.quantity / (factor or 1.0),
            precision_rounding=self.secondary_uom_id.uom_id.rounding,
        )
        if (
            float_compare(
                self.secondary_uom_qty,
                qty,
                precision_rounding=self.secondary_uom_id.uom_id.rounding,
            )
            != 0
        ):
            self.secondary_uom_qty = qty

    @api.onchange("product_uom_id")
    def onchange_product_uom_id_for_secondary(self):
        if not self.secondary_uom_id:
            return
        factor = self.product_uom_id.factor * self.secondary_uom_id.factor
        qty = float_round(
            self.quantity / (factor or 1.0),
            precision_rounding=self.product_uom_id.rounding,
        )
        if (
            float_compare(
                self.secondary_uom_qty,
                qty,
                precision_rounding=self.product_uom_id.rounding,
            )
            != 0
        ):
            self.secondary_uom_qty = qty
