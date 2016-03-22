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

from dateutil.relativedelta import relativedelta

from openerp import models, fields, api
from openerp.tools.float_utils import float_round

import openerp.addons.decimal_precision as dp


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
        if self.env.context.get('currency_id'):
            currency = self.env['res.currency'].browse(
                self.env.context['currency_id'])
        else:
            currency = self.env.user.company_id.currency_id
        prec = currency.decimal_places
        if self.value == 'fixed':
            return float_round(self.value_amount, precision_digits=prec)
        elif self.value == 'percent':
            amt = total_amount * (self.value_amount / 100.0)
            if self.amount_round:
                amt = float_round(amt, precision_rounding=self.amount_round)
            return float_round(amt, precision_digits=prec)
        elif self.value == 'balance':
            return float_round(remaining_amount,  precision_digits=prec)
        return None


class AccountPaymentTerm(models.Model):
    _inherit = "account.payment.term"

    @api.one
    def compute(self, value, date_ref=False):
        """Complete overwrite of compute method to add rounding on line
        computing and also to handle weeks and months
        """
        date_ref = date_ref or fields.Date.today()
        amount = value
        result = []
        if self.env.context.get('currency_id'):
            currency = self.env['res.currency'].browse(
                self.env.context['currency_id'])
        else:
            currency = self.env.user.company_id.currency_id
        prec = currency.decimal_places
        for line in self.line_ids:
            amt = line.compute_line_amount(value, amount)
            if not amt:
                continue
            next_date = fields.Date.from_string(date_ref)
            if line.option == 'day_after_invoice_date':
                next_date += relativedelta(days=line.days,
                                           weeks=line.weeks,
                                           months=line.months)
            elif line.option == 'fix_day_following_month':
                next_date += relativedelta(days=line.days,
                                           weeks=line.weeks,
                                           months=line.months)
                # Getting 1st of next month
                next_first_date = next_date + relativedelta(day=1, months=1)
                next_date = next_first_date + relativedelta(days=line.days - 1)
            elif line.option == 'last_day_following_month':
                # Getting last day of next month
                next_date += relativedelta(day=31, months=1)
            elif line.option == 'last_day_current_month':
                # Getting last day of next month
                next_date += relativedelta(day=31, months=0)
            result.append((fields.Date.to_string(next_date), amt))
            amount -= amt
        amount = reduce(lambda x, y: x + y[1], result, 0.0)
        dist = round(value - amount, prec)
        if dist:
            last_date = result and result[-1][0] or fields.Date.today()
            result.append((last_date, dist))
        return result
