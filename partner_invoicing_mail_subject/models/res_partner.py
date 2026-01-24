# Copyright 2026 NICO SOLUTIONS - ENGINEERING & IT
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

import re

from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    invoice_email_subject = fields.Char(
        string="Individual invoice mail subject",
        translate=True,
        help=(
            "Optional: Define a custom subject line for invoice emails for "
            "this partner. You can use placeholders like {invoice_number}, "
            "{partner_name}, or {invoice_date}. If left empty, the standard "
            "email template subject will be used."
        ),
    )

    @api.onchange("invoice_email_subject")
    def _onchange_invoice_email_subject(self):
        if not self.invoice_email_subject:
            return

        allowed_keys = {"invoice_number", "partner_name", "invoice_date"}
        keys_in_text = set(
            re.findall(r"\{([a-zA-Z0-9_]+)\}", self.invoice_email_subject)
        )
        invalid_keys = keys_in_text - allowed_keys
        if invalid_keys:
            invalid_keys_formatted = [f"{{{k}}}" for k in invalid_keys]
            allowed_keys_formatted = [f"{{{k}}}" for k in allowed_keys]

            title = self.env._("Invalid placeholders")
            message_template = self.env._(
                "The following placeholders are invalid and will "
                "not be replaced:\n{invalid}\n"
                "Allowed placeholders: {allowed}"
            )
            message = message_template.format(
                invalid=", ".join(invalid_keys_formatted),
                allowed=", ".join(allowed_keys_formatted),
            )

            return {
                "warning": {
                    "title": title,
                    "message": message,
                }
            }
