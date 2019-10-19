# Copyright 2013-2016 Camptocamp SA (Yannick Vaucher)
# Copyright 2004-2016 Odoo S.A. (www.odoo.com)
# Copyright 2015-2016 Akretion
# (Alexis de Lattre <alexis.delattre@akretion.com>)
# Copyright 2018 Simone Rubino - Agile Business Group
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import calendar
from functools import reduce

from dateutil.relativedelta import relativedelta

from odoo import _, api, exceptions, fields, models
from odoo.exceptions import ValidationError
from odoo.tools.float_utils import float_is_zero, float_round


class AccountPaymentTermHoliday(models.Model):
    _name = "account.payment.term.holiday"
    _description = "Payment Term Holidays"

    payment_id = fields.Many2one(comodel_name="account.payment.term")
    holiday = fields.Date(required=True)
    date_postponed = fields.Date(string="Postponed date", required=True)

    @api.constrains("holiday", "date_postponed")
    def check_holiday(self):
        if fields.Date.from_string(self.date_postponed) <= fields.Date.from_string(
            self.holiday
        ):
            raise ValidationError(
                _("Holiday %s can only be postponed into the future") % self.holiday
            )
        if (
            self.search_count(
                [
                    ("payment_id", "=", self.payment_id.id),
                    ("holiday", "=", self.holiday),
                ]
            )
            > 1
        ):
            raise ValidationError(
                _("Holiday %s is duplicated in current payment term") % self.holiday
            )
        if (
            self.search_count(
                [
                    ("payment_id", "=", self.payment_id.id),
                    "|",
                    ("date_postponed", "=", self.holiday),
                    ("holiday", "=", self.date_postponed),
                ]
            )
            >= 1
        ):
            raise ValidationError(
                _("Date %s cannot is both a holiday and a Postponed date")
                % self.holiday
            )


class AccountPaymentTermLine(models.Model):
    _inherit = "account.payment.term.line"

    amount_round = fields.Float('Amount Rounding', digits='Account')
    months = fields.Integer(string="Number of Months")
    weeks = fields.Integer(string="Number of Weeks")

    def compute_line_amount(self, total_amount, remaining_amount, precision_digits):
        """Compute the amount for a payment term line.
        In case of procent computation, use the payment
        term line rounding if defined

            :param total_amount: total balance to pay
            :param remaining_amount: total amount minus sum of previous lines
                computed amount
            :returns: computed amount for this line
        """
        self.ensure_one()
        if self.value == "fixed":
            return float_round(self.value_amount, precision_digits=precision_digits)
        elif self.value == "percent":
            amt = total_amount * (self.value_amount / 100.0)
            if self.amount_round:
                amt = float_round(amt, precision_rounding=self.amount_round)
            return float_round(amt, precision_digits=precision_digits)
        elif self.value == "balance":
            return float_round(remaining_amount, precision_digits=precision_digits)
        return None

    def _decode_payment_days(self, days_char):
        # Admit space, dash and comma as separators
        days_char = days_char.replace(" ", "-").replace(",", "-")
        days_char = [x.strip() for x in days_char.split("-") if x]
        days = [int(x) for x in days_char]
        days.sort()
        return days

    @api.constrains("payment_days")
    def _check_payment_days(self):
        if not self.payment_days:
            return
        try:
            payment_days = self._decode_payment_days(self.payment_days)
            error = any(day <= 0 or day > 31 for day in payment_days)
        except Exception:
            error = True
        if error:
            raise exceptions.Warning(_("Payment days field format is not valid."))

    payment_days = fields.Char(
        string="Payment day(s)",
        help="Put here the day or days when the partner makes the payment. "
        "Separate each possible payment day with dashes (-), commas (,) "
        "or spaces ( ).",
    )


class AccountPaymentTerm(models.Model):
    _inherit = "account.payment.term"

    sequential_lines = fields.Boolean(
        string="Sequential lines",
        default=False,
        help="Allows to apply a chronological order on lines.",
    )
    holiday_ids = fields.One2many(
        string="Holidays",
        comodel_name="account.payment.term.holiday",
        inverse_name="payment_id",
    )

    def apply_holidays(self, date):
        holiday = self.holiday_ids.search(
            [("payment_id", "=", self.id), ("holiday", "=", date)]
        )
        if holiday:
            return fields.Date.from_string(holiday.date_postponed)
        return date

    def apply_payment_days(self, line, date):
        """Calculate the new date with days of payments"""
        if line.payment_days:
            payment_days = line._decode_payment_days(line.payment_days)
            if payment_days:
                new_date = None
                payment_days.sort()
                days_in_month = calendar.monthrange(date.year, date.month)[1]
                for day in payment_days:
                    if date.day <= day:
                        if day > days_in_month:
                            day = days_in_month
                        new_date = date + relativedelta(day=day)
                        break
                if not new_date:
                    day = payment_days[0]
                    if day > days_in_month:
                        day = days_in_month
                    new_date = date + relativedelta(day=day, months=1)
                return new_date
        return date

    def compute(self, value, date_ref=False):
        """Complete overwrite of compute method to add rounding on line
        computing and also to handle weeks and months
        """
        date_ref = date_ref or fields.Date.today()
        amount = value
        result = []
        if self.env.context.get("currency_id"):
            currency = self.env["res.currency"].browse(self.env.context["currency_id"])
        else:
            currency = self.env.user.company_id.currency_id
        prec = currency.decimal_places
        next_date = fields.Date.from_string(date_ref)
        for line in self.line_ids:
            amt = line.compute_line_amount(value, amount, prec)
            if not self.sequential_lines:
                # For all lines, the beginning date is `date_ref`
                next_date = fields.Date.from_string(date_ref)
                if float_is_zero(amt, precision_rounding=prec):
                    continue
            if line.option == "day_after_invoice_date":
                next_date += relativedelta(
                    days=line.days, weeks=line.weeks, months=line.months
                )
            elif line.option == "after_invoice_month":
                # Getting 1st of next month
                next_first_date = next_date + relativedelta(day=1, months=1)
                next_date = next_first_date + relativedelta(
                    days=line.days - 1, weeks=line.weeks, months=line.months
                )
            elif line.option == "day_following_month":
                # Getting last day of next month
                next_date += relativedelta(day=line.days, months=1)
            elif line.option == "day_current_month":
                # Getting last day of next month
                next_date += relativedelta(day=line.days, months=0)
            next_date = self.apply_payment_days(line, next_date)
            next_date = self.apply_holidays(next_date)
            if not float_is_zero(amt, precision_rounding=prec):
                result.append((fields.Date.to_string(next_date), amt))
                amount -= amt
        amount = reduce(lambda x, y: x + y[1], result, 0.0)
        dist = round(value - amount, prec)
        if dist:
            last_date = result and result[-1][0] or fields.Date.today()
            result.append((last_date, dist))
        return result
