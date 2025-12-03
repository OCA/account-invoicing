# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class AccountMoveLine(models.Model):

    _inherit = "account.move.line"

    def _update_product_supplier_name(self):
        for rec in self:
            if not rec.name or not rec.product_id or not rec.product_id.seller_ids:
                continue
            seller = rec.product_id.seller_ids.filtered(
                lambda s: s.partner_id == rec.move_id.partner_id
                and (
                    s.product_id == rec.product_id
                    or s.product_tmpl_id == rec.product_id.product_tmpl_id
                )
            )
            seller.product_name = rec.name

    def action_select_purchase_line(self):
        self.ensure_one()
        if self.purchase_line_id:
            purchase_order = self.purchase_line_id.order_id
        else:
            order_ref = self.move_id.invoice_origin
            purchase_order = self.env["purchase.order"].search(
                [
                    "|",
                    ("name", "=", order_ref),
                    ("partner_ref", "=", order_ref),
                    ("state", "in", ("purchase", "done")),
                ]
            )
        context = {
            **self.env.context,
            **{
                "default_move_line_id": self.id,
                "default_purchase_order_id": purchase_order.id
                if purchase_order
                else False,
            },
        }
        return {
            "type": "ir.actions.act_window",
            "name": "Select Purchase Line",
            "res_model": "account.move.line.select.purchase.line.wizard",
            "view_mode": "form",
            "target": "new",
            "context": context,
        }
