# Copyright 2013-2017 Agile Business Group sagl
#     (<http://www.agilebg.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class AccountInvoiceLine(models.Model):
    _inherit = "account.move.line"

    def _compute_product_customer_code(self):
        product_customerinfo_obj = self.env["product.customerinfo"]
        for line in self:
            code_id = product_customerinfo_obj.browse()
            if line.move_id.is_sale_document():
                product = line.product_id
                code_id = product_customerinfo_obj.search(
                    [
                        ("product_tmpl_id", "=", product.product_tmpl_id.id),
                        ("name", "=", line.move_id.partner_id.id),
                    ],
                    limit=1,
                )
            line.product_customer_code = code_id.product_code or ""

    product_customer_code = fields.Char(
        compute="_compute_product_customer_code",
        string="Product Customer Code",
    )
