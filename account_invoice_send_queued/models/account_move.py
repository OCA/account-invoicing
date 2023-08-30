# Copyright 2023 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    email_send_job_ids = fields.Many2many(
        comodel_name="queue.job",
        column1="invoice_id",
        column2="job_id",
        string="Email Send Jobs",
        relation="account_move_email_send_job_rel",
        copy=False,
    )

    def action_invoice_send_email_job(self):
        self.ensure_one()
        action = self.with_context(discard_logo_check=True).action_invoice_sent()
        ctx = dict(self.env.context.copy(), **action["context"])
        # pylint: disable=W8121
        composer = self.env["account.invoice.send"].with_context(ctx).create({})
        composer.onchange_template_id()
        composer._send_email()
