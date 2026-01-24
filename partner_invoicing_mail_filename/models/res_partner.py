import re

from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    invoice_pdf_filename = fields.Char(
        string="Invoice PDF Filename",
        translate=True,
        help=(
            "Partner-specific invoice PDF filename.\n"
            "You can use the following placeholders which will be replaced dynamically "
            "when generating the PDF filename:\n\n"
            "  {invoice_number}  → The invoice reference\n"
            "  {partner_name}    → The partner name\n"
            "  {invoice_date}    → The invoice date\n\n"
            "  {default}         → The default filename will be added\n\n"
            "Example:\n"
            "  Invoice_{invoice_number}_{partner_name}  → "
            "Invoice_RE_2026_0001_John Doe.pdf\n\n"
            "This allows you to customize filenames per partner without touching code. "
            "If left empty, the default report filename is used."
        ),
    )

    @api.onchange("invoice_pdf_filename")
    def _onchange_invoice_pdf_filename(self):
        if not self.invoice_pdf_filename:
            return

        allowed_keys = {"invoice_number", "partner_name", "invoice_date", "default"}
        keys_in_text = set(
            re.findall(r"\{([a-zA-Z0-9_]+)\}", self.invoice_pdf_filename)
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
