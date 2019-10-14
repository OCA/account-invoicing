# Copyright 2013-2017 Agile Business Group sagl
#     (<http://www.agilebg.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    @api.multi
    def _get_product_customer_code(self):
        product_supplierinfo_obj = self.env['product.supplierinfo']
        for line in self.filtered(lambda il: il.product_id.supplier_ids):
            product = line.product_id
            code_id = product_supplierinfo_obj.search([
                ('supplierinfo_type', '=', 'customer'),
                ('product_tmpl_id', '=', product.product_tmpl_id.id),
                ('name', '=', line.invoice_id.partner_id.id)
            ], limit=1)
            line.product_customer_code = code_id.product_code or ''

    product_customer_code = fields.Char(
        compute='_get_product_customer_code',
        string='Product Customer Code',
        size=64
    )
