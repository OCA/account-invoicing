# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Yannick Vaucher
#    Copyright 2013 Camptocamp SA
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
from openerp.osv import orm, fields


class AccountConfigSettings(orm.TransientModel):
    _inherit = 'account.config.settings'

    _columns = {
        'tax_calculation_rounding': fields.related(
            'company_id',
            'tax_calculation_rounding',
            type='float',
            string='Tax Rounding unit'),
        'tax_calculation_rounding_method': fields.related(
            'company_id',
            'tax_calculation_rounding_method',
            type='selection',
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
                 "total amount with taxes."),
        'tax_calculation_rounding_account_id': fields.related(
            'company_id',
            'tax_calculation_rounding_account_id',
            type='many2one',
            relation='account.account',
            string='Tax Rounding account',
            domain=[('type', '<>', 'view')]),
    }

    _defaults = {
        'tax_calculation_rounding': 0.05
    }

    def onchange_company_id(self, cr, uid, ids, company_id, context=None):
        res = super(AccountConfigSettings, self
                    ).onchange_company_id(cr, uid, ids,
                                          company_id, context=context)
        company = self.pool.get('res.company').browse(cr, uid, company_id,
                                                      context=context)
        res['value']['tax_calculation_rounding'] = company.tax_calculation_rounding
        res['value']['tax_calculation_rounding_account_id'] = company.tax_calculation_rounding_account_id.id
        return res
