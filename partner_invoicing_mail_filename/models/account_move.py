from odoo import models


class AccountMove(models.Model):
    _inherit = "account.move"

    def _get_invoice_report_filename(self, extension="pdf", report=None):
        """
        Return partner-specific filename with placeholders replaced,
        supports {default}, and respects the commercial partner's language.
        """
        self.ensure_one()
        commercial_p = self.partner_id.commercial_partner_id
        if commercial_p.invoice_pdf_filename:
            # Use commercial partner language to match invoice recipients filename
            partner_lang = commercial_p.lang or "en_US"
            template = commercial_p.with_context(lang=partner_lang).invoice_pdf_filename
            format_kwargs = {
                "invoice_number": self.name or "",
                "partner_name": self.partner_id.name or "",
                "invoice_date": self.invoice_date.strftime("%Y-%m-%d")
                if self.invoice_date
                else "",
            }
            if "{default}" in template:
                core_filename = (
                    super()
                    ._get_invoice_report_filename(extension=extension, report=report)
                    .rsplit(".", 1)[0]
                )
                format_kwargs["default"] = core_filename

            file_name = template.format(**format_kwargs).strip()
            safe_file_name = file_name.replace("/", "_")
            return f"{safe_file_name}.{extension}"

        return super()._get_invoice_report_filename(extension=extension, report=report)
