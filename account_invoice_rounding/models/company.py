# -*- coding: utf-8 -*-
# Copyright 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from odoo import models, fields


class ResCompany(models.Model):
    _inherit = 'res.company'

    tax_calculation_rounding = fields.Float('Tax Rounding unit')
    tax_calculation_rounding_account_id = fields.Many2one(
        'account.account',
        'Tax Rounding Account',
        domain=[('internal_type', '<>', 'view')]
    )
    tax_calculation_rounding_method = fields.Selection(
        [('round_per_line', 'Round per Line'),
         ('round_globally', 'Round Globally'),
         ('swedish_round_globally', 'Swedish Round globally'),
         ('swedish_add_invoice_line', 'Swedish Round by adding a line'),
         ],
        string='Tax Calculation Rounding Method',
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
