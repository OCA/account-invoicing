import logging

from dateutil.relativedelta import relativedelta

from odoo import models, fields, api

_logger = logging.getLogger(__name__)


class InvoiceMergeAutoPartner(models.Model):
    _inherit = 'res.partner'

    invoice_merge_recurring_rule_type = fields.Selection(
        [('daily', 'Day(s)'),
         ('weekly', 'Week(s)'),
         ('monthly', 'Month(s)'),
         ('monthlylastday', 'Month(s) last day'),
         ('yearly', 'Year(s)'),
         ],
        default='monthly', copy=False,
        string='Merged invoice recurrence rule',
        help="Specify Interval for automatic invoice merge.",
    )

    invoice_merge_recurring_interval = fields.Integer(
        default=1, copy=False, required=True,
        string='Merged invoicing recurrence number',
        help="Repeat merged invoicing every (Days/Week/Month/Year)",
    )

    invoice_merge_next_date = fields.Date(
        String='Invoice merge next date',
        help='Next merged invoicing date',
        copy=False, index=True,
    )

    @api.multi
    def _invoice_merge_increment_next_date(self):
        "Increment invoice merge next date according to recurrence settings"
        for partner in self:
            old_date = partner.invoice_merge_next_date
            if old_date:
                interval = self.invoice_merge_time_interval(
                    partner.invoice_merge_recurring_rule_type,
                    partner.invoice_merge_recurring_interval,
                )
                partner.invoice_merge_next_date = (
                    fields.Date.from_string(old_date) + interval)

    @api.model
    def invoice_merge_time_interval(self, recurring_rule_type, interval):
        """ Compute and return a time interval from given recurrence params.

        Courtesy of contract module authors.
        """
        if recurring_rule_type == 'daily':
            return relativedelta(days=interval)
        elif recurring_rule_type == 'weekly':
            return relativedelta(weeks=interval)
        elif recurring_rule_type == 'monthly':
            return relativedelta(months=interval)
        elif recurring_rule_type == 'monthlylastday':
            return relativedelta(months=interval, day=31)
        else:
            return relativedelta(years=interval)
