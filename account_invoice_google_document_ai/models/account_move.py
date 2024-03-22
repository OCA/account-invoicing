# Copyright 2023 CreuBlanca
# Copyright 2023 ForgeFlow
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    can_send_to_ocr = fields.Boolean(compute="_compute_can_send_to_ocr")

    @api.depends("state", "move_type", "company_id")
    def _compute_can_send_to_ocr(self):
        for move in self:
            move.can_send_to_ocr = move._get_can_send_to_ocr()

    def _get_can_send_to_ocr(self):
        return (
            self.is_purchase_document()
            and self.state == "draft"
            and self.company_id.ocr_google_enabled != "no_send"
        )

    def ocr_process(self):
        self.ensure_one()
        attachments = self.message_main_attachment_id
        if attachments and attachments.exists() and self.can_send_to_ocr:
            self.env["account.move.google.document.ai"]._update_invoice_from_attachment(
                attachments[0], self
            )

    def _get_create_invoice_from_attachment_decoders(self):
        res = super()._get_create_invoice_from_attachment_decoders()
        if self.env.company.ocr_google_enabled == "send_automatically":
            res.append(
                (
                    90,
                    self.env[
                        "account.move.google.document.ai"
                    ]._create_invoice_from_attachment,
                )
            )
        return res

    def _get_update_invoice_from_attachment_decoders(self, invoice):
        res = super()._get_update_invoice_from_attachment_decoders(invoice)
        if self.env.company.ocr_google_enabled == "send_automatically":
            res.append(
                (
                    90,
                    self.env[
                        "account.move.google.document.ai"
                    ]._update_invoice_from_attachment,
                )
            )
        return res
