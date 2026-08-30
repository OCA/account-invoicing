# Copyright 2026 NICO SOLUTIONS - ENGINEERING & IT
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo import models


class AccountMove(models.Model):
    _inherit = "account.move"

    def _get_invoice_report_filename(self, extension="pdf", report=None):
        self.ensure_one()
        commercial_p = self.partner_id.commercial_partner_id
        file_name = ""
        if commercial_p.invoice_pdf_filename:
            partner_lang = commercial_p.lang or "en_US"
            template = commercial_p.with_context(
                lang=partner_lang,
                object=self,
            ).invoice_pdf_filename
            file_name = self._render_filename_template(template)

        if file_name:
            safe_file_name = file_name.replace("/", "_")
            return f"{safe_file_name}.{extension}"

        return super()._get_invoice_report_filename(extension=extension, report=report)

    def _render_filename_template(self, template):
        self.ensure_one()
        try:
            result = (
                self.env["mail.template"]
                .with_context(object=self)
                ._render_template(
                    template,
                    "account.move",
                    [self.id],
                )
            )
            return result.get(self.id) or ""
        except Exception:
            return ""
