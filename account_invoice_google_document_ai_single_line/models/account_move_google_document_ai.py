from odoo import models


class AccountMoveGoogleDocumentAi(models.AbstractModel):
    _inherit = "account.move.google.document.ai"

    def _process_invoice(self, invoice, invoice_data, messages):
        """Inherit method for add single invoice line."""
        if (
            invoice_data["write"]
            and self.env.company.google_ocr_invoice_mode == "single_line_total"
        ):
            if invoice_data["write"].get("invoice_line_ids"):
                invoice_data["write"].pop("invoice_line_ids")
            amount_total = invoice_data["control"].get("amount_total")
            invoice.write({"quick_edit_total_amount": amount_total})
        return super()._process_invoice(invoice, invoice_data, messages)

    def _create_invoice_from_attachment(self, attachment):
        """Inherit method for remove tax from the invoice without tax."""
        invoice = super()._create_invoice_from_attachment(attachment)
        if not invoice:
            return invoice
        if self.env.company.google_ocr_invoice_mode != "single_line_total":
            return invoice
        invoice_data = self._get_ocr_data(attachment)
        if invoice_data and not invoice_data["control"].get("amount_tax"):
            invoice.with_context(without_tax=True)._onchange_quick_edit_total_amount()
            return invoice
        invoice._onchange_quick_edit_total_amount()
        return invoice

    def _update_invoice_from_attachment(self, attachment, invoice):
        """Inherit method for remove tax from the invoice without tax."""
        super()._update_invoice_from_attachment(attachment, invoice)
        if (
            self.env.company.google_ocr_invoice_mode != "single_line_total"
            or not invoice
        ):
            return True
        invoice_data = self._get_ocr_data(attachment)
        if invoice_data and not invoice_data["control"].get("amount_tax"):
            invoice.with_context(without_tax=True)._onchange_quick_edit_total_amount()
            return True
        invoice._onchange_quick_edit_total_amount()
        return True
