# Copyright 2026 Moduon Team S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl-3.0).

from odoo import fields, models


class AccountMoveSendBatchWizard(models.TransientModel):
    _inherit = "account.move.send.batch.wizard"

    mail_template_id = fields.Many2one(
        "mail.template",
        store=True,
        readonly=False,
        domain=[("model_id", "=", "account.move")],
    )

    def action_send_and_print(self):
        res = super().action_send_and_print()
        if not self.mail_template_id:
            return res
        sending_data = fields.first(self.move_ids).sending_data
        sending_data.update({"mail_template_id": self.mail_template_id.id})
        self.move_ids.sending_data = sending_data
        return res
