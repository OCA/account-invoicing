# Copyright 2021 Camptocamp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    def _prepare_account_move_line(self, move=False):
        res = super()._prepare_account_move_line(move)
        res["external_name"] = res["name"]
        product_id = res.get("product_id")
        if product_id:
            product = self.env["product.product"].browse(product_id)
            if product.accounting_description:
                res["name"] = product.accounting_description
        return res
