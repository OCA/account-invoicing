# -*- coding: utf-8 -*-
# Copyright 2015 Alessio Gerace <alessio.gerace@agilebg.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openerp import models, fields


class RoundingByCurrency(models.Model):
    _name = 'company.rounding'

    company_id = fields.Many2one('res.company', 'Company', required=True)
    currency_id = fields.Many2one('res.currency', 'Currency', required=True)
    tax_calculation_rounding = fields.Float('Tax Rounding Precision')
    tax_calculation_rounding_account_id = fields.Many2one(
        'account.account',
        'Tax Rounding Account',
        domain=[('type', '<>', 'view')]
    )
    tax_calculation_rounding_method = fields.Selection(
        [
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
        "total amount with taxes."
    )

    _sql_constraints = [
        ('currency_id_uniq_per_company', 'unique (currency_id, company_id)',
            'Currency must be unique per Company!'),
    ]


class ResCompany(models.Model):
    _inherit = 'res.company'

    currency_rounding_rules = fields.One2many(
        'company.rounding', 'company_id',
        'Rounding Rule'
    )
