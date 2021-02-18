from odoo import _, api, exceptions, fields, models
from datetime import datetime

MONTHS_SELECTION = [
    ('01', 'January'), ('02', 'February'), ('03', 'March'), ('04', 'April'),
    ('05', 'May'), ('06', 'June'), ('07', 'July'), ('08', 'August'),
    ('09', 'September'), ('10', 'October'), ('11', 'November'), ('12', 'December')
]


class PaymentTerm(models.Model):
    _inherit = "account.payment.term"

    def date_ranges_are_present(self):
        for line in self.line_ids:
            if line.based_on_date_ranges and line.date_range_ids:
                return True
        return False

    @api.multi
    @api.constrains("line_ids")
    def _check_date_ranges(self):
        for term in self:
            if term.date_ranges_are_present():
                for line in term.line_ids:
                    if not line.date_range_ids:
                        raise exceptions.ValidationError(
                            _("Term %s: every line must have date ranges."))

    @api.one
    def compute(self, value, date_ref=False):
        if not self.date_ranges_are_present():
            # we must use [0] because of api.one
            return super(PaymentTerm, self).compute(value, date_ref)[0]
        date_ref = date_ref or fields.Date.today()
        amount = value
        sign = value < 0 and -1 or 1
        result = []
        if self.env.context.get('currency_id'):
            currency = self.env['res.currency'].browse(self.env.context['currency_id'])
        else:
            currency = self.env.user.company_id.currency_id
        for line in self.line_ids:
            if line.value == 'fixed':
                amt = sign * currency.round(line.value_amount)
            elif line.value == 'percent':
                amt = currency.round(value * (line.value_amount / 100.0))
            elif line.value == 'balance':
                amt = currency.round(amount)
            if amt:
                next_date = fields.Date.from_string(date_ref)
                next_date = line.apply_date_ranges_days(next_date)
                result.append((fields.Date.to_string(next_date), amt))
                amount -= amt
        amount = sum(amt for _, amt in result)
        dist = currency.round(value - amount)
        if dist:
            last_date = result and result[-1][0] or fields.Date.today()
            result.append((last_date, dist))
        return result


class AccountPaymentTermLine(models.Model):
    _inherit = "account.payment.term.line"

    date_range_ids = fields.One2many(
        "account.payment.term.line.date.range", "term_line_id",
        "Date ranges for due date",
        help="Setting a date range here allows to establish the corresponding due "
             "date when payment must be done.\nExample: "
             "from 1 Jan to 31 Mar > due date 20 May")
    based_on_date_ranges = fields.Boolean("Based on date ranges")

    def apply_date_ranges_days(self, date):
        """Calculate the new date acording to date ranges"""
        for dr in self.date_range_ids:
            due_date = dr.get_appliable_due_date(date)
            if due_date:
                return due_date
        return date


class AccountPaymentTermLineDateRange(models.Model):
    _name = "account.payment.term.line.date.range"
    _description = "Payment term line date range"
    _rec_name = "due_date_month"

    due_date_day = fields.Integer("Due date day", required=True)
    due_date_month = fields.Selection(
        MONTHS_SELECTION, "Due date month", required=True)
    start_date_day = fields.Integer("Start date day", required=True, default=1)
    start_date_month = fields.Selection(
        MONTHS_SELECTION, "Start date month", required=True, default="01")
    end_date_day = fields.Integer("End date day", required=True)
    end_date_month = fields.Selection(
        MONTHS_SELECTION, "End date month", required=True)
    term_line_id = fields.Many2one(
        "account.payment.term.line", "Payment term line", ondelete="cascade")

    def get_appliable_due_date(self, date):
        current_year = date.year
        start_date = datetime(
            current_year, int(self.start_date_month), self.start_date_day).date()
        end_date = datetime(
            current_year, int(self.end_date_month), self.end_date_day).date()
        if end_date >= date >= start_date:
            due_date = datetime(
                current_year, int(self.due_date_month), self.due_date_day).date()
            if due_date < date:
                due_date = datetime(
                    current_year + 1, int(self.due_date_month), self.due_date_day
                ).date()
            return due_date
        else:
            return False
