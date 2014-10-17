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
from datetime import datetime
from dateutil.relativedelta import relativedelta
import time

from openerp.osv import orm, fields
from openerp.tools.float_utils import float_round

import openerp.addons.decimal_precision as dp
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT


class AccountPaymentTermLine(orm.Model):
    _inherit = "account.payment.term.line"
    _columns = {
        'amount_round': fields.float(
            'Amount Rounding',
            digits_compute=dp.get_precision('Account'),
            help="Sets the amount so that it is a multiple of this value.\n"
                 "To have amounts that end in 0.99, set rounding 1, "
                 "surcharge -0.01"),
    }

    def compute_line_amount(self, cr, uid, id, total_amount, remaining_amount,
                            context=None):
        """Compute the amount for a payment term line.
        In case of procent computation, use the payment
        term line rounding if defined

            :param total_amount: total balance to pay
            :param remaining_amount: total amount minus sum of previous lines
                computed amount
            :returns: computed amount for this line
        """
        if isinstance(id, (tuple, list)):
            assert len(id) == 1, "compute_line_amount accepts only 1 ID"
            id = id[0]
        obj_precision = self.pool.get('decimal.precision')
        prec = obj_precision.precision_get(cr, uid, 'Account')
        line = self.browse(cr, uid, id, context=context)
        if line.value == 'fixed':
            return float_round(line.value_amount, precision_digits=prec)
        elif line.value == 'procent':
            amt = total_amount * line.value_amount
            if line.amount_round:
                amt = float_round(amt, precision_rounding=line.amount_round)
            return float_round(amt, precision_digits=prec)
        elif line.value == 'balance':
            amt = float_round(remaining_amount, precision_digits=prec)
        return None


class AccountPaymentTerm(orm.Model):
    _inherit = "account.payment.term"

    def compute(self, cr, uid, id, value, date_ref=False, context=None):
        """Complete overwrite of compute method to add rounding on line
        computing.
        """
        obj_precision = self.pool['decimal.precision']
        prec = obj_precision.precision_get(cr, uid, 'Account')
        if not date_ref:
            date_ref = datetime.now().strftime(DEFAULT_SERVER_DATE_FORMAT)
        pt = self.browse(cr, uid, id, context=context)
        amount = value
        result = []
        for line in pt.line_ids:
            amt = line.compute_line_amount(value, amount)
            if not amt:
                continue
            next_date = (datetime.strptime(date_ref,
                                           DEFAULT_SERVER_DATE_FORMAT) +
                         relativedelta(days=line.days))
            if line.days2 < 0:
                # Getting 1st of next month
                next_first_date = next_date + relativedelta(day=1, months=1)
                next_date = next_first_date + relativedelta(days=line.days2)
            if line.days2 > 0:
                next_date += relativedelta(day=line.days2, months=1)
            result.append(
                (next_date.strftime(DEFAULT_SERVER_DATE_FORMAT), amt))
            amount -= amt

        amount = reduce(lambda x, y: x + y[1], result, 0.0)
        dist = round(value - amount, prec)
        if dist:
            result.append((time.strftime(DEFAULT_SERVER_DATE_FORMAT), dist))
        return result
