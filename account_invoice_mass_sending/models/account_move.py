# Copyright 2019 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, fields, models


class AccountInvoice(models.Model):
    _inherit = "account.move"

    sending_in_progress = fields.Boolean(
        default=False,
        help="If checked, the invoice is already being processed, "
        "and it will prevent the sending of a duplicated mail.",
    )

    def mass_sending(self, template=None):
        """
        This method triggers the asynchronous sending for the selected
        invoices for which there is no asynchronous sending in progress
        and an email address is defined.
        """
        invoices_to_send = self.filtered(
            lambda i: not i.sending_in_progress and i.partner_id.email
        )
        if invoices_to_send:
            invoices_to_send.write(
                {
                    "sending_in_progress": True,
                }
            )
            for invoice in invoices_to_send:
                description = _("Send invoice %(name)s by email", name=invoice.name)
                invoice.with_delay(
                    description=description,
                    channel="root.account_invoice_mass_sending_channel",
                )._send_invoice_individually(template=template)
        return invoices_to_send

    def _send_invoice_individually(self, template=None):
        self.ensure_one()
        res = self.action_invoice_sent()
        wiz_ctx = res["context"] or {}
        wiz_ctx.update(
            {
                "active_model": self._name,
                "active_ids": self.ids,
                "discard_logo_check": True,
                "account_invoice_mass_sending": True,
            }
        )
        wiz = self.env["account.invoice.send"].with_context(**wiz_ctx).create({})
        wiz.write(
            {
                "is_print": False,
                "is_email": True,
                "template_id": template.id,
                "composition_mode": "comment",
            }
        )
        wiz.onchange_template_id()
        self.write(
            {
                "sending_in_progress": False,
            }
        )
        return wiz.send_and_print_action()
