# Copyright 2015 Agile Business Group sagl (https://www.agilebg.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo import models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    def _get_computed_name(self):
        line_description = super()._get_computed_name()

        if self.product_id and self.user_has_groups(
            "account_invoice_line_description."
            "group_use_product_description_per_inv_line"
        ):
            product = self.product_id.with_context(lang=self.move_id.partner_id.lang)
            if self.move_id.is_purchase_document():
                line_description = product.description_purchase or self.name
            elif self.move_id.is_sale_document():
                line_description = product.description_sale or self.name
            if line_description:
                return line_description
        return line_description
