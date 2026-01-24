# Copyright 2026 NICO SOLUTIONS - ENGINEERING & IT
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo import api, models


class AccountMoveSend(models.AbstractModel):
    _inherit = "account.move.send"

    @api.model
    def _get_default_mail_subject(self, move, mail_template, mail_lang):
        """
        Return partner-specific subject if set, else default.
        Only applies if the commercial partner's invoice sending method is 'email'.
        """
        if move._name == "account.move" and move.move_type in (
            "out_invoice",
            "out_refund",
        ):
            commercial = move.partner_id.commercial_partner_id
            if (
                commercial.invoice_sending_method == "email"
                and commercial.invoice_email_subject
            ):
                values = {
                    "invoice_number": move.name.replace("/", "_"),
                    "partner_name": commercial.name,
                    "invoice_date": move.invoice_date.strftime("%Y-%m-%d")
                    if move.invoice_date
                    else "",
                }
                return commercial.invoice_email_subject.format(**values)

        return super()._get_default_mail_subject(move, mail_template, mail_lang)
