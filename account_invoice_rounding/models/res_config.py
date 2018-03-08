# -*- coding: utf-8 -*-
# Copyright 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from odoo import models, fields, api


class AccountConfigSettings(models.TransientModel):
    _inherit = 'account.config.settings'

    tax_calculation_rounding = fields.Float(
        related='company_id.tax_calculation_rounding',
        string='Tax Rounding unit',
        default=0.05)
    tax_calculation_rounding_method = fields.Selection(
        related='company_id.tax_calculation_rounding_method',
        selection=[
                ('round_per_line', 'Round per line'),
                ('round_globally', 'Round globally'),
                ('swedish_round_globally', 'Swedish Round globally'),
                ('swedish_add_invoice_line',
                 'Swedish Round by adding an invoice line'),
            ],
        string='Tax calculation rounding method',
        help="If you select 'Round per line' : for each tax, the tax "
             "amount will first be computed and rounded for each "
             "PO/SO/invoice line and then these rounded amounts will be "
             "summed, leading to the total amount for that tax. If you "
             "select 'Round globally': for each tax, the tax amount will "
             "be computed for each PO/SO/invoice line, then these amounts"
             " will be summed and eventually this total tax amount will "
             "be rounded. If you sell with tax included, you should "
             "choose 'Round per line' because you certainly want the sum "
             "of your tax-included line subtotals to be equal to the "
             "total amount with taxes.")
    tax_calculation_rounding_account_id = fields.Many2one(
        related='company_id.tax_calculation_rounding_account_id',
        comodel='account.account',
        string='Tax Rounding account',
        domain=[('internal_type', '<>', 'view')])

    @api.onchange('company_id')
    def onchange_company_id(self):
        res = super(AccountConfigSettings, self).onchange_company_id()
        if self.company_id:
            company = self.company_id
            self.tax_calculation_rounding = company.tax_calculation_rounding
            self.tax_calculation_rounding_account_id = \
                company.tax_calculation_rounding_account_id.id
        return res
