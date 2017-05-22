# -*- coding: utf-8 -*-
# © 2016 Nicola Malcontenti - Agile Business Group
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo import models, fields, api


class AccountInvoiceLine(models.Model):

    _inherit = 'account.invoice.line'
    product_customer_code = fields.Char(
        'Product Customer Code', compute='_compute_customer_code')

    @api.one
    def _compute_customer_code(self):
        code = u''
        product_customer_code_obj = self.env['product.customer.code']
        partner = self.partner_id
        product = self.product_id
        if product and partner:
            code_ids = product_customer_code_obj.search([
                ('product_id', '=', product.id),
                ('partner_id', '=', partner.id)], limit=1)
            if code_ids:
                code = product_customer_code_obj.browse(
                    code_ids[0].id).product_code or ''
        self.product_customer_code = code
