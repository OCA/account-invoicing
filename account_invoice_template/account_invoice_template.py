# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2017 Aurium Technologies (<http://www.auriumtechnologies.com>)
#    Copyright (C) 2011 Agile Business Group sagl (<http://www.agilebg.com>)
#    Copyright (C) 2011 Domsense srl (<http://www.domsense.com>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from odoo import fields, models, api


class account_invoice_template(models.Model):

    _inherit = 'account.document.template'
    _name = 'account.invoice.template'

    partner_id = fields.Many2one(
        comodel_name='res.partner', string='Partner', required=True)
    account_id = fields.Many2one(
        comodel_name='account.account', string='Account', required=True)
    template_line_ids = fields.One2many(
        comodel_name='account.invoice.template.line', inverse_name='template_id', string='Template Lines')
    invoice_type = fields.Selection(selection=[
        ('out_invoice', 'Customer Invoice'),
        ('in_invoice', 'Supplier Invoice'),
        ('out_refund', 'Customer Refund'),
        ('in_refund', 'Supplier Refund'),
    ], string='Type', required=True)


class account_invoice_template_line(models.Model):

    _name = 'account.invoice.template.line'
    _inherit = 'account.document.template.line'

    account_id = fields.Many2one(
        comodel_name='account.account', string='Account', required=True)
    analytic_account_id = fields.Many2one(
        comodel_name='account.analytic.account', string='Analytic Account', ondelete="cascade")
    invoice_line_tax_id = fields.Many2many(
        'account.tax', 'account_invoice_template_line_tax', 'invoice_line_id', 'tax_id', 'Taxes')
    template_id = fields.Many2one(
        comodel_name='account.invoice.template', string='Template', ondelete='cascade')
    product_id = fields.Many2one(
        comodel_name='product.product', string='Product')

    _sql_constraints = [
        ('sequence_template_uniq', 'unique (template_id,sequence)',
            'The sequence of the line must be unique per template !')
    ]

    @api.onchange("product_id")
    def product_id_change(self):

        result = {}
        product_obj = self.env['product.product']
        account_obj = self.env['account.account']

        for rec in self:

            if not rec.product_id:
                return {}
            product = product_obj.browse(rec.product_id)
            # name
            result.update({'name': product.id.name})
            # account
            rec.account_id = False

            if rec.template_id.invoice_type in ('out_invoice', 'out_refund'):
                rec.account_id = product.id.product_tmpl_id.property_account_income_id
                if not rec.account_id:
                    rec.account_id = product.id.categ_id.property_account_income_categ_id
            else:
                rec.account_id = product.id.product_tmpl_id.property_account_expense_id
                if not rec.account_id:
                    rec.account_id = product.id.categ_id.property_account_expense_categ_id
            if rec.account_id:
                result['account_id'] = rec.account_id

            # taxes
            taxes = rec.account_id and account_obj.browse(
                rec.account_id.id).tax_ids or False
            if rec.template_id.invoice_type in ('out_invoice', 'out_refund') and product.id.taxes_id:
                taxes = product.id.taxes_id
            elif product.id.supplier_taxes_id:
                taxes = product.id.supplier_taxes_id
            rec.tax_ids = taxes and [tax.id for tax in taxes] or False
            result.update({'invoice_line_tax_id': rec.tax_ids})

            return {'value': result}
