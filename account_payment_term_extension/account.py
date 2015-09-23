# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Yannick Vaucher
#    Copyright 2013 Camptocamp SA
#    Copyright (C) 2004-2010 OpenERP S.A. (www.odoo.com)
#    Copyright (C) 2015 Akretion (http://www.akretion.com)
#    @author Alexis de Lattre <alexis.delattre@akretion.com>
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

from openerp import models, fields, api
from openerp.tools.float_utils import float_round

import openerp.addons.decimal_precision as dp
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT


class AccountPaymentTermLine(models.Model):
    _inherit = "account.payment.term.line"

    amount_round = fields.Float(
        string='Amount Rounding',
        digits=dp.get_precision('Account'),
        # TODO : I don't understand this help msg ; what is surcharge ?
        help="Sets the amount so that it is a multiple of this value.\n"
             "To have amounts that end in 0.99, set rounding 1, "
             "surcharge -0.01")
    months = fields.Integer(string='Number of Months')
    weeks = fields.Integer(string='Number of Weeks')
    start_with_end_month = fields.Boolean(
        string='Start by End of Month',
        help="If you have a payment term 'End of month 45 days' "
        "(which is not the same as '45 days end of month' !), you "
        "should activate this option and then set "
        "'Number of days' = 45 and 'Day of the month' = 0.")

    @api.multi
    def compute_line_amount(self, total_amount, remaining_amount):
        """Compute the amount for a payment term line.
        In case of procent computation, use the payment
        term line rounding if defined

            :param total_amount: total balance to pay
            :param remaining_amount: total amount minus sum of previous lines
                computed amount
            :returns: computed amount for this line
        """
        self.ensure_one()
        prec = self.env['decimal.precision'].precision_get('Account')
        if self.value == 'fixed':
            return float_round(self.value_amount, precision_digits=prec)
        elif self.value == 'procent':
            amt = total_amount * self.value_amount
            if self.amount_round:
                amt = float_round(amt, precision_rounding=self.amount_round)
            return float_round(amt, precision_digits=prec)
        elif self.value == 'balance':
            return float_round(remaining_amount,  precision_digits=prec)
        return None


class AccountPaymentTerm(models.Model):
    _inherit = "account.payment.term"

    def compute(self, cr, uid, id, value, date_ref=False, context=None):
        """Complete overwrite of compute method to add rounding on line
        computing and also to handle weeks and months
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

            next_date = fields.Date.from_string(date_ref)
            if line.start_with_end_month:
                next_date += relativedelta(day=1, months=1, days=-1)
            next_date += relativedelta(
                days=line.days, weeks=line.weeks, months=line.months)
            if line.days2 < 0:
                # Getting 1st of next month
                next_date += relativedelta(day=1, months=1, days=line.days2)
            if line.days2 > 0:
                next_date += relativedelta(day=line.days2, months=1)
            result.append(
                (fields.Date.to_string(next_date), amt))
            amount -= amt

        amount = reduce(lambda x, y: x + y[1], result, 0.0)
        dist = round(value - amount, prec)
        if dist:
            result.append((time.strftime(DEFAULT_SERVER_DATE_FORMAT), dist))
        return result
