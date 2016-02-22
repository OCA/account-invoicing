# -*- coding: utf-8 -*-
# © 2016 Akretion (http://www.akretion.com)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields


class AccountTax(models.Model):
    _inherit = 'account.tax'

    zugferd_type_code = fields.Selection([
        ('VAT', 'VAT'),
        ('ZF_INSURANCE_TAX', 'Insurance Tax'),
        ('AAJ', 'Tax on replacement part'),
        ], string='ZUGFeRD Type Code', default='VAT')
    zugferd_categ_code = fields.Selection([
        ('S', 'Standard Rate (S)'),
        ('IC', 'Intra-Community Supply (IC)'),
        ('O', 'Services outside scope of tax (O)'),
        ('Z', 'Zero rated goods (Z)'),
        ('E', 'Exempt from tax (E)'),
        ('AE', 'VAT Reverse Charge (AE)'),
        ], string='ZUGFeRD Category Code')
