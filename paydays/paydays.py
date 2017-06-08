# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2009 Albert Cervera i Areny (http://www.nan-tic.com).
#    All Rights Reserved
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from datetime import datetime
import dateutil.relativedelta as relativedelta
import calendar
from openerp import models, api, fields
from openerp.exceptions import ValidationError


class AccountPaymentTerm(models.Model):

    _inherit = "account.payment.term"

    @api.one
    @api.constrains('payment_days')
    def _check_payment_days(self):
        days = self.payment_days
        if days:
            # Admit space, dash and colon separators.
            days = days.replace(' ', '-').replace(',', '-')
            days = [x.strip() for x in days.split('-') if x]
            try:
                days = [int(x) for x in days]
            except:
                raise ValidationError("Payment days field format is not "
                                      "valid.")

            for day in days:
                if day <= 0 or day > 31:
                    raise ValidationError("Payment days field format is not "
                                          "valid.")

    payment_days = fields.Char('Payment days', size=11,
                               help="If a company has more than one payment "
                                    "days in a month you should fill them in "
                                    "this field and set 'Day of the Month' "
                                    "field in line to zero. For example, "
                                    "if a company pays the 5th and 20th days "
                                    "of the month you should write '5-20' "
                                    "here.")

    @api.one
    def compute(self, value, date_ref=False):
        result = super(AccountPaymentTerm, self).compute(value, date_ref)
        term = self
        if not term.payment_days:
            return result

        # Admit space, dash and colon separators.
        days = term.payment_days.replace(' ', '-').replace(',', '-')
        days = [x.strip() for x in days.split('-') if x]
        if not days:
            return result
        days = [int(x) for x in days]
        days.sort()
        new_result = []
        for line in result[0]:
            new_date = None
            date_calc = datetime.strptime(line[0], '%Y-%m-%d')
            days_in_month = calendar.monthrange(date_calc.year,
                                                date_calc.month)[1]
            for day in days:
                if date_calc.day <= day:
                    if day > days_in_month:
                        day = days_in_month
                    new_date = date_calc + relativedelta.relativedelta(day=day)
                    break
            if not new_date:
                day = days[0]
                if day > days_in_month:
                    day = days_in_month
                new_date = date_calc + relativedelta.relativedelta(day=day,
                                                                   months=+1)
            new_result.append((new_date.strftime('%Y-%m-%d'), line[1]))
        return new_result
