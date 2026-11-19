# Copyright 2026 Moduon Team S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl-3.0).

from odoo import fields, models


class AccountMoveSendBatchWizard(models.TransientModel):
    _inherit = "account.move.send.batch.wizard"

    mail_template_id = fields.Many2one(
        "mail.template", domain=[("model", "=", "account.move")]
    )

    def action_send_and_print(self, force_synchronous=False, allow_fallback_pdf=False):
        if not self.mail_template_id:
            return super().action_send_and_print(
                force_synchronous=force_synchronous,
                allow_fallback_pdf=allow_fallback_pdf,
            )
        if force_synchronous:
            # The native method sends the invoices right away and clears their
            # ``sending_data``: the template can only be given through the context.
            return super(
                AccountMoveSendBatchWizard,
                self.with_context(
                    account_invoice_send_template_id=self.mail_template_id.id
                ),
            ).action_send_and_print(
                force_synchronous=force_synchronous,
                allow_fallback_pdf=allow_fallback_pdf,
            )
        res = super().action_send_and_print(
            force_synchronous=force_synchronous, allow_fallback_pdf=allow_fallback_pdf
        )
        # Asynchronous: the invoices are only flagged, the cron sends them later.
        for move in self.move_ids:
            move.sending_data = {
                **(move.sending_data or {}),
                "mail_template_id": self.mail_template_id.id,
            }
        return res
