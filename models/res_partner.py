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
        default='monthly', copy=False, required=True,
        string='Merged invoice recurrence rule',
        help="Specify Interval for automatic invoice merge.",
    )

    invoice_merge_recurring_interval = fields.Integer(
        default=1, copy=False, required=True,
        string='Merged invoicing recurrence number',
        help="Repeat merged invoicing every (Days/Week/Month/Year)",
    )

    invoice_merge_next_date = fields.Date(
        String=u'Invoice merge next date',
        help=u'Next merged invoicing date',
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

    @api.model
    def _invoice_merge_candidates(self, merge_date):
        invoices = self.env['account.invoice'].search([
            ('partner_id.invoice_merge_next_date', '<=', merge_date),
            ('state', '=', 'draft'),
            ('auto_merge', '=', True),
            ('date_invoice', '<=', merge_date),
        ])

        # `merge_date` may exceed `invoice_merge_next_date` if
        # current cron task is not executed often enough:
        return invoices.filtered(lambda inv: (
            inv.date_invoice <= inv.partner_id.invoice_merge_next_date))

    @api.model
    def _cron_invoice_merge(self, merge_date=None):
        """Automatically merge invoices based on partner preferences and
        increment the next invoice merge date.
        """
        if merge_date is None:
            merge_date = fields.Date.today()
        _logger.debug('Executing _cron_merge_invoices with merge date %s',
                      merge_date)

        invoices = self._invoice_merge_candidates(merge_date)
        for partner in invoices.mapped('partner_id'):
            partner._invoice_merge_increment_next_date()
        return invoices, invoices.do_merge(date_invoice=merge_date)
