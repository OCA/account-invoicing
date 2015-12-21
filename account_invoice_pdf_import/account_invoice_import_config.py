# -*- coding: utf-8 -*-
##############################################################################
#
#    Account Invoice PDF import module for Odoo
#    Copyright (C) 2015 Akretion (http://www.akretion.com)
#    @author Alexis de Lattre <alexis.delattre@akretion.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
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

from openerp import models, fields, api, _
from openerp.exceptions import ValidationError


class AccountInvoiceImportConfig(models.Model):
    _name = 'account.invoice.import.config'
    _description = 'Configuration for the import of Supplier Invoice'

    name = fields.Char(string='Name', required=True)
    partner_ids = fields.One2many(
        'res.partner', 'invoice_import_id',
        string='Partners')
    active = fields.Boolean(default=True)
    invoice_line_method = fields.Selection([
        ('static_product', 'Static Product'),
        ('auto_product', 'Auto-selected Product'),
        ('no_product', 'Without Product'),
        ], string='Method for Invoice Line', required=True,
        default='no_product')
    company_id = fields.Many2one(
        'res.company', string='Company',
        ondelete='cascade', required=True,
        default=lambda self: self.env['res.company']._company_default_get(
            'account.invoice.import.config'))
    account_id = fields.Many2one(
        'account.account', string='Expense Account',
        domain=[('type', 'not in', ('view', 'closed'))])
    account_analytic_id = fields.Many2one(
        'account.analytic.account', string='Analytic Account',
        domain=[('type', '!=', 'view')])
    label = fields.Char(
        string='Force Description', help="Force invoice line description")
    tax_ids = fields.Many2many(
        'account.tax', string='Taxes',
        domain=[('type_tax_use', 'in', ('all', 'purchase'))])
    static_product_id = fields.Many2one(
        'product.product', string='Static Product')

    @api.constrains('invoice_line_method', 'account_id', 'static_product_id')
    def _check_import_config(self):
        for config in self:
            if (
                    config.invoice_line_method == 'static_product' and
                    not config.static_product_id):
                raise ValidationError(_(
                    "Static Product must be set on the invoice import "
                    "configuration of supplier '%s' that has a Method "
                    "for Invoice Line set to 'Static Product'.")
                    % config.partner_id.name)
            if (
                    config.invoice_line_method == 'no_product' and
                    not config.account_id):
                raise ValidationError(_(
                    "The Expense Account must be set on the invoice "
                    "import configuration of supplier '%s' that has a "
                    "Method for Invoice Line set to 'Without product'.")
                    % config.partner_id.name)
