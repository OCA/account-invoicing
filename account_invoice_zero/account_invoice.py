# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Guewen Baconnier
#    Copyright 2014 Camptocamp SA
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

from functools import partial

from openerp.osv import orm
from openerp.tools.float_utils import float_is_zero


class account_invoice(orm.Model):
    _inherit = 'account.invoice'

    def invoice_validate(self, cr, uid, ids, context=None):
        result = super(account_invoice, self).invoice_validate(
            cr, uid, ids, context=context)
        dp_obj = self.pool['decimal.precision']
        precision = dp_obj.precision_get(cr, uid, 'Account')
        is_zero = partial(float_is_zero, precision_digits=precision)
        for invoice in self.browse(cr, uid, ids, context=context):
            if is_zero(invoice.amount_total):
                account = invoice.account_id.id
                # search the payable / receivable lines
                lines = [line for line in invoice.move_id.line_id
                         if line.account_id.id == account]
                # reconcile the lines with a zero balance
                if is_zero(sum(line.debit - line.credit for line in lines)):
                    move_line_obj = self.pool['account.move.line']
                    move_line_obj.reconcile(cr, uid,
                                            [line.id for line in lines],
                                            context=context)
        return result
