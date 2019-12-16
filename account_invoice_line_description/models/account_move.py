# Copyright 2015 Agile Business Group sagl (https://www.agilebg.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo import api, models


class AccountMove(models.Model):
    _inherit = "account.move.line"

    @api.onchange("product_id")
    def _onchange_product_id(self):
        res = super(AccountMove, self)._onchange_product_id()
        if self.product_id and self.user_has_groups(
            "account_invoice_line_description."
            "group_use_product_description_per_inv_line"
        ):
            inv_type = self.move_id.type
            product = self.product_id.with_context(lang=self.move_id.partner_id.lang)
            self.name = (
                product.description_purchase or self.name
                if inv_type in ("in_invoice", "in_refund")
                else product.description_sale or self.name
            )
        return res
