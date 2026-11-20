# Copyright 2026 Swanand Beedkar
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class AccountMoveSendWizard(models.TransientModel):
    _inherit = "account.move.send.wizard"

    @api.depends("move_id.invoice_recipient_ids")
    def _compute_mail_partners(self):
        res = super()._compute_mail_partners()
        for wizard in self:
            if (
                wizard.move_id.is_sale_document(include_receipts=True)
                and wizard.move_id.invoice_recipient_ids
            ):
                recipients = wizard.move_id.invoice_recipient_ids
                if not self.env.context.get("allow_partners_without_mail"):
                    recipients = recipients.filtered("email")
                wizard.mail_partner_ids = (
                    wizard.mail_partner_ids or self.env["res.partner"]
                ) | recipients
        return res
