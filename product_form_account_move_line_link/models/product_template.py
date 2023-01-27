# Copyright 2023 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    account_move_lines_count = fields.Float(
        compute="_compute_account_move_lines_count", string="Invoiced"
    )

    @api.depends("product_variant_ids.account_move_lines_count")
    def _compute_account_move_lines_count(self):
        for product in self:
            product.account_move_lines_count = sum(
                p.account_move_lines_count
                for p in product.with_context(active_test=False).product_variant_ids
            )
