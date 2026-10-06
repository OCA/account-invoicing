# Copyright 2015 Agile Business Group sagl (https://www.agilebg.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo import models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    def _compute_name(self):
        names = {line: line.name for line in self}
        super()._compute_name()
        if not self.env.user.has_group(
            "account_invoice_line_description."
            "group_use_product_description_per_inv_line"
        ):
            return
        for line in self:
            if (
                not line.product_id
                or line.display_type != "product"
                or line.move_id.inalterable_hash
            ):
                continue
            product = line.product_id.with_context(
                lang=line.move_id.partner_id.lang
                or line.partner_id.lang
                or self.env.lang
            )
            description = False
            if line.move_id.is_purchase_document():
                description = product.description_purchase
            elif line.move_id.is_sale_document():
                description = product.description_sale
            if description and (
                not names[line]
                or names[line] != line.name
                or names[line] == description
            ):
                line.name = description
