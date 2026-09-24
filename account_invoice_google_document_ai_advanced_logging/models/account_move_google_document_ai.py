import base64
import json
from datetime import datetime

from odoo import models


class AccountMoveGoogleDocumentAi(models.AbstractModel):
    _inherit = "account.move.google.document.ai"

    def _create_invoice_from_attachment(self, attachment):
        """Inherit to log OCR entities to chatter if the company setting is enabled."""
        invoice = super()._create_invoice_from_attachment(attachment)
        if not (invoice and self.env.company.log_ocr_entities_debug):
            return invoice
        invoice_data = self._get_ocr_data(attachment)
        # If Log ocr entities debug is enabled, log the OCR entities to
        # chatter.
        if self.env.company.log_ocr_entities_debug:
            self._log_ocr_entities_to_chatter(invoice, invoice_data)
        return invoice

    def _update_invoice_from_attachment(self, attachment, invoice):
        """Inherit to log OCR entities to chatter if the company setting is enabled."""
        res = super()._update_invoice_from_attachment(attachment, invoice)
        if not self.env.company.log_ocr_entities_debug:
            return res
        invoice_data = self._get_ocr_data(attachment)
        # If Log ocr entities debug is enabled, log the OCR entities to
        # chatter.
        if self.env.company.log_ocr_entities_debug:
            self._log_ocr_entities_to_chatter(invoice, invoice_data)
        return True

    def _log_ocr_entities_to_chatter(self, invoice, invoice_data):
        """New method to log OCR entities as JSON in the invoice chatter. #Issue-1"""
        json_content = json.dumps(invoice_data, indent=2, ensure_ascii=False)
        filename = f"ocr_entities_{datetime.now().strftime('%Y-%m-%d_%H:%M:%S')}.json"
        encoded_data = base64.b64encode(json_content.encode("utf-8"))
        attachment_values = self._prepare_attachment_values(
            filename, encoded_data, invoice
        )
        self.env["ir.attachment"].create(attachment_values)

    def _prepare_attachment_values(self, filename, encoded_data, invoice):
        """New method to prepare attachment values for logging OCR entities. #Issue-1"""
        attachment_values = {
            "name": filename,
            "type": "binary",
            "mimetype": "application/json",
            "datas": encoded_data,
            "res_id": invoice.id,
            "res_model": "account.move",
        }
        return attachment_values
