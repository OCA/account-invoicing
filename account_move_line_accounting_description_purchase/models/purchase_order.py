from odoo import models


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    def _prepare_account_move_line(self, move=False):
        res = super()._prepare_account_move_line(self, move=False)
        res["external_name"] = res["name"]
        product = self.env["product.template"].search([("id", "=", res["product_id"])])
        if product.accounting_description:
            res["name"] = product.accounting_description
        return res
