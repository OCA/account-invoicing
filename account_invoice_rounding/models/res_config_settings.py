# Copyright 2016 Camptocamp SA
# Copyright 2020 initOS GmbH <https://initos.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

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
