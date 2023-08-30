# Copyright 2023 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models

from odoo.addons.queue_job.job import identity_exact


class AccountInvoiceSend(models.TransientModel):
    _inherit = "account.invoice.send"

    def enqueue_invoice_email_send(self):
        queue_obj = self.env["queue.job"]
        for invoice in self.invoice_ids:
            new_delay = invoice.with_delay(
                identity_key=identity_exact,
                channel="root.invoice_email_send_queue",
                description="Send invoice {} by email".format(invoice.name),
            ).action_invoice_send_email_job()
            job = queue_obj.search([("uuid", "=", new_delay.uuid)])
            invoice.sudo().email_send_job_ids = [(4, job.id)]
