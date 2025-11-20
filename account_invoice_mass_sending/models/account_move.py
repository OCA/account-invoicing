# Copyright 2019 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    sending_in_progress = fields.Boolean(
        default=False,
        help="If checked, the invoice is already being processed, "
        "and it will prevent the sending of a duplicated mail.",
    )

    def mass_sending(self, template=None):
        """
        Trigger asynchronous sending for selected invoices.
        
        Only sends invoices that:
        - Are not already being sent
        - Have a partner email address
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
        """Send a single invoice using account.move.send wizard."""
        self.ensure_one()
        
        # Get the action from account.move
        res = self.action_post_open()
        wiz_ctx = res.get("context") or {}
        wiz_ctx.update(
            {
                "active_model": self._name,
                # Setting both active_id and active_ids is required,
                # mimicking how direct call to ir.actions.act_window works
                "active_ids": self.ids,
                "active_id": self.id,
                "account_invoice_mass_sending": True,
            }
        )
        
        # Create wizard with proper context
        wiz_vals = {
            "checkbox_download": False,
            "checkbox_send_mail": True,
            "mode": "invoice_single",
        }
        
        # Add template only if provided
        if template:
            wiz_vals["mail_template_id"] = template.id
        
        wiz = (
            self.env["account.move.send"]
            .with_context(**wiz_ctx)
            .create(wiz_vals)
        )
        
        # Mark as no longer in progress
        self.write(
            {
                "sending_in_progress": False,
            }
        )
        
        return wiz.action_send_and_print(allow_fallback_pdf=True)