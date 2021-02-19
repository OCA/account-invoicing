# Copyright (C) 2019 - Today: Commown (https://commown.coop)
# @author: Florent Cayré
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, api, fields, _
from odoo.exceptions import ValidationError

from odoo.addons.queue_job.job import job
from odoo.addons.queue_job.job import identity_exact
import logging
_logger = logging.getLogger(__name__)


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    auto_merge = fields.Boolean(
        # Override label and help only
        string="Pay automatically",
        help="Pay automatically at partner's next merge date",
    )
    merge_auto_pay_job_ids = fields.Many2many(
        comodel_name='queue.job',
        column1='invoice_id',
        column2='job_id',
        string="Merge Auto Payment Jobs",
        copy=False,
    )

    @api.constrains("auto_merge", "payment_mode_id")
    def _check_auto_merge(self):
        for inv in self:
            if inv.auto_merge and not inv.payment_mode_id:
                raise models.ValidationError(
                    _("Payment mode is needed to auto pay an invoice"))

    @api.model
    @job(default_channel='root.account_invoice_merge_auto_pay_queued')
    def _invoice_merge_auto_pay_invoice_job(self):
        """ Open the invoice and post a payment
        """
        self.ensure_one()
        _logger.info(
            "_invoice_merge_auto_pay_invoice_job executed for invoice %d", self.id)
        self.exists().action_invoice_open()
        if self.state != "paid":  # Avoid crash if, e.g. amount == 0
            payment = self._invoice_merge_payment()
            tx = payment._create_payment_transaction()
            tx.s2s_do_transaction()
            tx._set_transaction_done()
            tx._post_process_after_done()

    @api.model
    def _invoice_merge_payment(self):
        """ Use given invoice"s payment mode and its partner payment token to
        create and return a payment
        """
        self.ensure_one()
        pay_mode = self.payment_mode_id
        token = self.partner_id.payment_token_id
        if not token:
            raise ValidationError(_("No payment token for invoice id %s (%s)")
                                  % (self.id, self.number))
        return self.env["account.payment"].create({
            "partner_id": self.partner_id.id,
            "partner_type": "customer",
            "state": "draft",
            "payment_type": "inbound",
            "journal_id": pay_mode.fixed_journal_id.id,
            "payment_method_id": pay_mode.payment_method_id.id,
            "amount": self.amount_total,
            "currency_id": self.currency_id.id,
            "invoice_ids": [(6, 0, [self.id])],
            "payment_token_id": token.id,
            "communication": self.reference or self.number,
        })

    @api.model
    def _cron_invoice_merge(self, merge_date=None):
        """ Automatically pay invoices that were either:

        - the result invoice of a merge
        - or a candidate for a merge but were not merged
          (for instance because they were unique for the merge key)
        """

        invoices, merge_infos = super(
            AccountInvoice, self)._cron_invoice_merge(merge_date)

        for new_inv_id in merge_infos:
            new_inv = self.env["account.invoice"].browse(new_inv_id)
            if new_inv.type == "out_invoice":
                _logger.info(
                    "Automatically paying merged invoice %s (from %s)",
                    new_inv.id, merge_infos[new_inv.id])
                new_inv.with_delay(
                    identity_key=identity_exact
                )._invoice_merge_auto_pay_invoice_job()

        merged_invoice_ids = set(inv_id for inv_ids in list(merge_infos.values())
                                 for inv_id in inv_ids)
        for inv in invoices:
            if inv.type == "out_invoice" and inv.id not in merged_invoice_ids:
                _logger.info("Automatically paying non-merged inv %s", inv.id)
                inv.with_delay(
                    identity_key=identity_exact
                )._invoice_merge_auto_pay_invoice_job()

        return invoices, merge_infos
