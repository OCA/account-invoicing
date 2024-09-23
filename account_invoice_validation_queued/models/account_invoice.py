# Copyright 2019 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models

from odoo.addons.queue_job.job import job


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    validation_job_ids = fields.Many2many(
        comodel_name="queue.job",
        column1="invoice_id",
        column2="job_id",
        string="Validation Jobs",
        copy=False,
    )

    @job(default_channel="root.account_invoice_validation_queued")
    def action_invoice_open_job(self):
        self.ensure_one()
        if self.state not in {"draft", "sent"}:
            return
        self.action_invoice_open()
