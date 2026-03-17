# Copyright 2026 ACSONE SA/NV, BCIM
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    def _prepare_account_move_line(self, move=False):
        vals = super()._prepare_account_move_line(move=move)
        if self.product_packaging_id:
            vals.update(
                {
                    "product_packaging_id": self.product_packaging_id.id,
                    "product_packaging_qty": self.product_packaging_qty,
                }
            )
        return vals
