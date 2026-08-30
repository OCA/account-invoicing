# Copyright 2025 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models

from odoo.addons.account.models.ir_attachment import SUPPORTED_FILE_TYPES


class AccountMoveSend(models.AbstractModel):
    _inherit = "account.move.send"

    @api.model
    def _get_ubl_available_attachments(
        self, mail_attachments_widget, invoice_edi_format
    ):
        accepted_attachments, refused_attachments = (
            super()._get_ubl_available_attachments(mail_attachments_widget, invoice_edi_format)  # noqa
        )

        if self.move_id:
            add_attachments = self._get_invoice_additional_attachments(self.move_id)
            if add_attachments:
                ubl_format_info = (
                    self.env["res.partner"]
                    ._get_ubl_cii_formats_info()
                    .get(invoice_edi_format, {})
                )
                if not ubl_format_info.get("embed_attachments"):
                    refused_attachments += add_attachments
                else:
                    add_accepted = add_attachments.filtered(
                        lambda attachment: attachment.mimetype in SUPPORTED_FILE_TYPES
                    )
                    accepted_attachments += add_accepted
                    refused_attachments += add_attachments - add_accepted

        return accepted_attachments, refused_attachments

    @api.model
    def _get_invoice_additional_attachments(self, move):
        attachments = self.env["ir.attachment"].search(
            [
                ("res_id", "=", move.id),
                ("res_model", "=", move._name),
            ]
        )
        return attachments
