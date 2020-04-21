# Copyright 2019 Tecnativa - Pedro M. Baeza
# Copyright 2020 Tecnativa - Manuel Calero
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, exceptions, models

from odoo.addons.queue_job.job import identity_exact


class ValidateAccountMove(models.TransientModel):
    _inherit = "validate.account.move"

    def enqueue_invoice_confirm(self):
        queue_obj = self.env["queue.job"]
        active_ids = self.env.context.get("active_ids", [])
        moves = self.env["account.move"].browse(active_ids)
        move_to_post = moves.filtered(lambda m: m.state == "draft").sorted(
            lambda m: (m.date, m.ref or "", m.id)
        )
        # Check if all invoices are for the same date
        inv_date = move_to_post[:1].date
        if any(move_to_post.filtered(lambda x: x.date != inv_date)):
            raise exceptions.UserError(
                _("You can't enqueue invoices with different dates.")
            )
        for move in move_to_post:
            new_delay = move.with_delay(
                identity_key=identity_exact,
            ).action_invoice_open_job()
            job = queue_obj.search([("uuid", "=", new_delay.uuid)])
            move.sudo().validation_job_ids = [(4, job.id)]
