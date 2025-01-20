# Copyright 2023 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ProductProduct(models.Model):
    _inherit = "product.product"

    account_move_lines_count = fields.Integer(
        compute="_compute_account_move_lines_count", string="Invoiced"
    )

    def _compute_account_move_lines_count(self):
        if not self.env.user.has_group("account.group_account_invoice") or not self.ids:
            self.sudo().account_move_lines_count = 0
            return
        domain = [
            ("product_id", "in", self.ids),
            ("company_id", "in", self.env.companies.ids),
        ]
        account_move_line_data = self.env["account.move.line"].read_group(
            domain, ["product_id"], ["product_id"]
        )
        mapped_data = {
            m["product_id"][0]: m["product_id_count"] for m in account_move_line_data
        }
        for product in self:
            product.account_move_lines_count = mapped_data.get(product.id, 0)
