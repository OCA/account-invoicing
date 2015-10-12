# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2015 Agile Business Group sagl (<http://www.agilebg.com>)
#    Author: Alessio Gerace <alessio.gerace@agilebg.com>
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
from openerp import models, fields, api
from openerp.tools.float_utils import float_round, float_compare
from openerp.tools.translate import _

import openerp.addons.decimal_precision as dp


class AccountInvoice(models.Model):
    _inherit = "account.invoice"


    def _compute_swedish_rounding(self, cr, uid, invoice, context=None):
        """
        Depending on the method defined, we add an invoice line or adapt the
        tax lines to have a rounded total amount on the invoice
        :param invoice: invoice browse record
        :return dict: updated values for _amount_all
        """
        # avoid recusivity

        if 'swedish_write' in context:
            return {}
        rounding_rule_model = self.pool.get('company.rounding')
        company = invoice.company_id
        round_method = ''
        rounding_prec = 0.0
        if invoice.currency_id.id != company.currency_id.id:
            ret_ids = rounding_rule_model.search(
                cr, uid,
                [
                    ('company_id', '=', company.id),
                    ('currency_id', '=', invoice.currency_id.id),
                ],
                context=context)
            if ret_ids:
                rule = rounding_rule_model.browse(cr, uid, ret_ids[0], context=context)
                company.tax_calculation_rounding_method =(
                    rule.tax_calculation_rounding_method)
                company.tax_calculation_rounding = (
                    rule.tax_calculation_rounding)
                company.tax_calculation_rounding_account_id = (
                    rule.tax_calculation_rounding_account_id)
            else:
                return {}

        return super(AccountInvoice, self)._compute_swedish_rounding(
            cr, uid, invoice, context=context)



