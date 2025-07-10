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

    def mass_sending(self, template=None, include_followers=False):
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
                )._send_invoice_individually(
                    template=template,
                    include_followers=include_followers,
                )
        return invoices_to_send

    def _send_invoice_individually(self, template=None, include_followers=False):
        self.ensure_one()
        res = self.action_invoice_sent()
        wiz_ctx = res["context"] or {}
        wiz_ctx.update(
            {
                "active_model": self._name,
                # Setting both active_id and active_ids is required,
                # mimicking how direct call to ir.actions.act_window works
                "active_ids": self.ids,
                "active_id": self.id,
                "discard_logo_check": True,
                "include_followers": include_followers,
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

    def _notify_get_recipients(self, message, msg_vals, **kwargs):
        recipients_data = super()._notify_get_recipients(message, msg_vals, **kwargs)
        if self.env.context.get("include_followers", False):
            return recipients_data
        else:
            msg_sudo = message.sudo()
            pids = (
                msg_vals.get("partner_ids", [])
                if msg_vals
                else msg_sudo.partner_ids.ids
            )
            filtered_recipients_data = [
                recipient
                for recipient in recipients_data
                if recipient.get("id") in pids
            ]
            return filtered_recipients_data
