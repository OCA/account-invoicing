# Copyright 2026 Bright Haven Electric LLC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import models

_logger = logging.getLogger(__name__)


class AccountPaymentRegister(models.TransientModel):
    _inherit = "account.payment.register"

    def _invalidate_invoice_pdf_reports(self, moves):
        """Delete cached invoice PDF attachments so they are regenerated
        with the latest payment information on the next print or send action.

        This ensures that when a payment is registered against an invoice,
        the previously generated PDF (which may not reflect the payment)
        is removed so Odoo will create a fresh one upon the next
        Send & Print or Print action.
        """
        invoices = moves.filtered(
            lambda m: m.is_invoice(include_receipts=True)
            and m.invoice_pdf_report_id
        )
        if not invoices:
            return

        for invoice in invoices:
            attachment = invoice.invoice_pdf_report_id
            _logger.info(
                "Removing cached PDF attachment %s (id=%s) for invoice %s "
                "to allow regeneration after payment.",
                attachment.name,
                attachment.id,
                invoice.name,
            )
            attachment.unlink()
            invoice.invalidate_recordset(
                fnames=["invoice_pdf_report_id", "invoice_pdf_report_file"]
            )

    def action_create_payments(self):
        """Override to remove cached invoice PDFs before creating payments.

        The invoice PDF is generated once and cached as an ir.attachment.
        When a new payment is registered the cached PDF becomes stale
        because it does not reflect the updated payment status.  By
        unlinking the attachment here the next Send & Print (or Print)
        action will regenerate the PDF with the correct payment data.
        """
        # Collect the invoices linked to the payment lines *before*
        # creating the payments, since context / line_ids are still
        # available at this point.
        moves = self.line_ids.move_id
        self._invalidate_invoice_pdf_reports(moves)
        return super().action_create_payments()
