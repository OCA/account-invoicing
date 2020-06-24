import logging

from odoo import _, models, api
from odoo.exceptions import ValidationError

from odoo.addons.queue_job.job import job


_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = 'res.partner'

    _payment_task_duration = 2  # Estimated payment tx duration, in seconds

    @api.model
    def _invoice_merge_payment(self, invoice):
        """ Use given invoice's payment mode and its partner payment token to
        create and return a payment
        """
        pay_mode = invoice.payment_mode_id
        token = invoice.partner_id.payment_token_id
        if not token:
            raise ValidationError(_(u'No payment token for invoice id %s (%s)')
                                  % (invoice.id, invoice.number))
        return self.env['account.payment'].create({
            'partner_id': invoice.partner_id.id,
            'partner_type': 'customer',
            'state': 'draft',
            'payment_type': 'inbound',
            'journal_id': pay_mode.fixed_journal_id.id,
            'payment_method_id': pay_mode.payment_method_id.id,
            'amount': invoice.amount_total,
            'currency_id': invoice.currency_id.id,
            'invoice_ids': [(6, 0, [invoice.id])],
            'payment_token_id': token.id,
        })

    @api.model
    @job
    def _invoice_merge_auto_pay_invoice(self, invoice_id):
        " Open the invoice and post a payment "
        _logger.info('_invoice_merge_auto_pay_invoice executed for invoice %d',
                     invoice_id)
        invoice = self.env['account.invoice'].browse(invoice_id).exists()
        invoice.action_invoice_open()
        if invoice.state != 'paid':  # Avoid crash if, e.g. amount == 0
            self._invoice_merge_payment(invoice).post()

    @api.model
    def _cron_invoice_merge(self, merge_date=None):
        """ Automatically pay invoices that were either:

        - the result invoice of a merge
        - or a candidate for a merge but were not merged
          (for instance because they were unique for the merge key)
        """

        invoices, merge_infos = super(
            ResPartner, self)._cron_invoice_merge(merge_date)

        pay_delay = self.with_delay(eta=self._payment_task_duration)

        for new_inv_id in merge_infos:
            new_inv = self.env['account.invoice'].browse(new_inv_id)
            if new_inv.type == 'out_invoice':
                _logger.info(
                    'Automatically paying merged invoice %s (from %s)',
                    new_inv.id, merge_infos[new_inv.id])
                pay_delay._invoice_merge_auto_pay_invoice(new_inv.id)

        merged_invoice_ids = set(inv_id for inv_ids in merge_infos.values()
                                 for inv_id in inv_ids)
        for inv in invoices:
            if inv.type == 'out_invoice' and inv.id not in merged_invoice_ids:
                _logger.info('Automatically paying non-merged inv %s', inv.id)
                pay_delay._invoice_merge_auto_pay_invoice(inv.id)

        return invoices, merge_infos
