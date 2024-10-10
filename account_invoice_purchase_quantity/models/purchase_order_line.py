# Copyright 2016 Camptocamp SA
# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    def _prepare_account_move_line(self, move=False):
        # Update the new invoice line value with received quantity and
        # ordered quantity
        res = super()._prepare_account_move_line(move=move)
        res.update(
            {
                "purchase_line_qty_received": self.qty_received,
                "purchase_line_product_qty": self.product_qty,
            }
        )
        return res
