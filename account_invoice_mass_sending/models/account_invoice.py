# -*- coding: utf-8 -*-
# Copyright 2019 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.addons.queue_job.job import job
from odoo.exceptions import UserError

JOB_QUEUE_CHANNEL = "root.PREPARE_SEND_PRINT_INVOICE"
SEND_QUEUE_CHANNEL = "root.SEND_PRINT_INVOICE"


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    sending_in_progress = fields.Boolean(
        default=False,
        help="If checked, the invoice is already being processed, "
             "and it will prevent the sending of a duplicated mail.")

    @api.multi
    def mass_send_print(self):
        """
        This method triggers the asynchronous "Send & Print" for the selected
        invoices for which there is no asynchronous sending in progress.
        """
        invoices_to_send = self.filtered(lambda i: not i.sending_in_progress)
        in_progress_invoices_count = len(self) - len(invoices_to_send)
        title = _("Invoices: Send")
        if in_progress_invoices_count > 0:
            warn_msg = _(
                "The sending of {in_progress_invoices_count} invoices is "
                "already in progress."
            ).format(in_progress_invoices_count=in_progress_invoices_count)
            self.env.user.notify_info(title=title, message=warn_msg)
        if invoices_to_send:
            msg = _(
                "The sending of {invoices_count} invoices will be processed "
                "in background."
            ).format(invoices_count=len(invoices_to_send))
            self.env.user.notify_info(title=title, message=msg)
            invoices_to_send.write({"sending_in_progress": True})
            invoices_to_send.with_delay().do_prepare_send_print()

    @api.multi
    @job(default_channel=JOB_QUEUE_CHANNEL)
    def do_prepare_send_print(self):
        for rec in self:
            rec.with_delay().do_send_print()

    @api.multi
    @job(default_channel=SEND_QUEUE_CHANNEL)
    def do_send_print(self):
        for rec in self:
            if not rec.partner_id.email:
                raise UserError(_(
                    "Missing email address on customer '{customer_name}'."
                ).format(
                    customer_name=rec.partner_id.display_name
                ))
            action_invoice_wizard = rec.action_invoice_sent()
            ctx = action_invoice_wizard["context"]
            ctx.update(
                {
                    "active_id": rec.id,
                    "active_ids": rec.ids,
                    "active_model": "account.invoice",
                }
            )
            invoice_wizard = (
                self.env[action_invoice_wizard["res_model"]]
                .with_context(ctx)
                .create({})
            )
            invoice_wizard.onchange_template_id_wrapper()
            invoice_wizard.send_mail_action()
        self.write({"sending_in_progress": False})
