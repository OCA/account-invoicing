# Copyright 2016 Camptocamp SA
# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    purchase_line_qty_received = fields.Float(
        string="Received Qty",
        readonly=True,
        digits="Product Unit of Measure",
        compute="_compute_purchase_line_qty",
    )
    purchase_line_product_qty = fields.Float(
        string="Ordered Qty",
        readonly=True,
        digits="Product Unit of Measure",
        compute="_compute_purchase_line_qty",
    )

    @api.depends("purchase_line_id.qty_received", "purchase_line_id.product_qty")
    def _compute_purchase_line_qty(self):
        for rec in self:
            if not rec.purchase_line_id:
                rec.update(
                    {"purchase_line_qty_received": 0, "purchase_line_product_qty": 0}
                )
                continue
            rec.update(
                {
                    "purchase_line_qty_received": rec.purchase_line_id.qty_received,
                    "purchase_line_product_qty": rec.purchase_line_id.product_qty,
                }
            )
