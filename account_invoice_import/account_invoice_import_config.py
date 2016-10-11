# -*- coding: utf-8 -*-
# © 2015-2016 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields, api, _
from openerp.exceptions import ValidationError


class AccountInvoiceImportConfig(models.Model):
    _name = 'account.invoice.import.config'
    _description = 'Configuration for the import of Supplier Invoices'

    name = fields.Char(string='Name', required=True)
    partner_ids = fields.One2many(
        'res.partner', 'invoice_import_id',
        string='Partners')
    active = fields.Boolean(default=True)
    invoice_line_method = fields.Selection([
        ('1line_no_product', 'Single Line, No Product'),
        ('1line_static_product', 'Single Line, Static Product'),
        ('nline_no_product', 'Multi Line, No Product'),
        ('nline_static_product', 'Multi Line, Static Product'),
        ('nline_auto_product', 'Multi Line, Auto-selected Product'),
        ], string='Method for Invoice Line', required=True,
        default='1line_no_product',
        help="The multi-line methods will not work for PDF invoices "
        "that don't have an embedded XML file. "
        "The 'Multi Line, Auto-selected Product' method will only work with "
        "ZUGFeRD invoices at Comfort or Extended level, not at Basic level.")
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
        string='Force Description',
        help="Force supplier invoice line description")
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
