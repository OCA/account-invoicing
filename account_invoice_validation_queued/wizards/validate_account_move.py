# Copyright 2019 Tecnativa - Pedro M. Baeza
# Copyright 2020 Tecnativa - Manuel Calero
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models

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
        for move in move_to_post:
            new_delay = move.with_delay(
                identity_key=identity_exact,
            ).action_invoice_open_job()
            job = queue_obj.search([("uuid", "=", new_delay.uuid)])
            move.sudo().validation_job_ids = [(4, job.id)]
