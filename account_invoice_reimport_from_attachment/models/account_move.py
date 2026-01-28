# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, models
from odoo.exceptions import AccessError, UserError


class AccountMove(models.Model):
    _inherit = "account.move"

    def _can_reimport_from_attachment(self):
        self.ensure_one()
        if not self.env.user.has_group(
            "account_invoice_reimport_from_attachment."
            "group_invoice_reimport_from_attachment"
        ):
            raise AccessError(
                _("You are not allowed to re-import invoices from attachments.")
            )

        if self.state != "draft":
            raise UserError(_("You can only re-import lines on a draft invoice."))

    def action_open_reimport_wizard(self):
        self.ensure_one()
        self._can_reimport_from_attachment()
        return {
            "type": "ir.actions.act_window",
            "name": _("Reimport from Attachment"),
            "res_model": "account.move.reimport.attachment.wizard",
            "view_mode": "form",
            "target": "new",
            "context": {
                "default_move_id": self.id,
            },
        }

    def _reimport_from_attachment(self, attachment):
        self.ensure_one()
        self._can_reimport_from_attachment()
        self.invoice_line_ids.unlink()
        invoice = self.journal_id.with_context(
            default_journal_id=self.journal_id.id
        )._create_document_from_attachment(attachment.ids)
        invoice.invoice_line_ids.move_id = self.id
        attachment.write({"res_model": "account.move", "res_id": self.id})
        invoice.unlink()
        return True
