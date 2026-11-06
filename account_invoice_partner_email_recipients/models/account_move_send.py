# Copyright 2026 Swanand Beedkar
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class AccountMoveSend(models.AbstractModel):
    _inherit = "account.move.send"

    @api.model
    def _get_default_mail_partner_ids(self, move, mail_template, mail_lang):
        partners = super()._get_default_mail_partner_ids(move, mail_template, mail_lang)
        if move.is_sale_document(include_receipts=True) and move.invoice_recipient_ids:
            recipients = move.invoice_recipient_ids
            if not self.env.context.get("allow_partners_without_mail"):
                recipients = recipients.filtered("email")
            partners |= recipients
        return partners
