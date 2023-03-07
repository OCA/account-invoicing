# Copyright (C) 2020 - Today: Commown (https://commown.coop)
# @author: Florent Cayré
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models, fields
import logging
_logger = logging.getLogger(__name__)


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    auto_merge = fields.Boolean(
        default=False,
        string='Merge automatically',
        help="Merge automatically at partner's next merge date",
    )

    @api.model
    def _invoice_merge_candidates(self, merge_date):
        invoices = self.search([
            ('partner_id.invoice_merge_next_date', '<=', merge_date),
            ('state', '=', 'draft'),
            ('auto_merge', '=', True),
            '|', ('date_invoice', '=', False),
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
