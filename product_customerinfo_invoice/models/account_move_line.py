# Copyright 2013-2017 Agile Business Group sagl
#     (<http://www.agilebg.com>)
# Copyright 2021 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class AccountInvoiceLine(models.Model):
    _inherit = "account.move.line"

    product_customer_code = fields.Char(
        compute="_compute_product_customer_code",
    )

    @api.depends(
        "product_id", "move_id.partner_id", "move_id.partner_show_customer_code"
    )
    def _compute_product_customer_code(self):
        for line in self:
            if line.product_id and line.move_id.partner_show_customer_code:
                product = line.product_id
                code_id = product._select_customerinfo(partner=line.move_id.partner_id)
                line.product_customer_code = code_id.product_code or ""
            else:
                line.product_customer_code = ""
