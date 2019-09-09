# Copyright 2019 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, exceptions, models
from odoo.addons.queue_job.job import identity_exact


class AccountInvoiceConfirm(models.TransientModel):
    _inherit = "account.invoice.confirm"

    def enqueue_invoice_confirm(self):
        queue_obj = self.env['queue.job']
        active_ids = self.env.context.get('active_ids', [])
        invoices = self.env['account.invoice'].browse(active_ids)
        if invoices.filtered(lambda x: x.state not in 'draft'):
            # Let standard method to raise the exception about draft state
            return self.invoice_confirm()
        # Check if all invoices are for the same date
        inv_date = invoices[:1].date_invoice
        for invoice in invoices:
            if invoice.date_invoice != inv_date:
                raise exceptions.UserError(_(
                    "You can't enqueue invoices with different dates."
                ))
        for invoice in invoices:
            new_delay = invoice.with_delay(
                identity_key=identity_exact,
            ).action_invoice_open_job()
            job = queue_obj.search([('uuid', '=', new_delay.uuid)])
            invoice.sudo().validation_job_ids = [(4, job.id)]
