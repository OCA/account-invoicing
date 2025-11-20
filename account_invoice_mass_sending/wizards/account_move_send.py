# Copyright 2019 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, models


class AccountMoveSend(models.TransientModel):
    _inherit = "account.move.send"
    _name = "account.move.send"
    _description = "Account Move Send - Mass Sending"

    def enqueue_invoices(self):
        """
        Enqueue invoices for asynchronous mass sending.
        
        Triggers background job processing for invoices that are:
        - Not already in sending progress
        - Have a partner email address defined
        
        Returns:
            dict: Client action for notification display
        """
        active_ids = self.env.context.get("active_ids", [])
        if not active_ids:
            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": _("Warning"),
                    "message": _("No invoices selected."),
                    "type": "warning",
                    "next": {"type": "ir.actions.act_window_close"},
                },
            }
        
        invoices = self.env["account.move"].browse(active_ids)
        invoices_to_send = invoices.mass_sending(self.mail_template_id)
        ineligible_invoices = invoices - invoices_to_send
        
        title = _("Invoices: Mass sending")
        msg = _(
            "The sending of %(invoices_count)d invoices will be processed "
            "in background.",
            invoices_count=len(invoices_to_send),
        )
        
        notification = {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": title,
                "message": msg,
                "type": "success",
                "next": {"type": "ir.actions.act_window_close"},
            },
        }
        
        # Notify about ineligible invoices
        if ineligible_invoices:
            invoicelist = [invoice.name for invoice in ineligible_invoices]
            warn_msg = _(
                "Invoices %(ineligible_invoices)s were already in "
                "processing or do not have an email address defined.",
                ineligible_invoices=", ".join(invoicelist),
            )
            notification["params"]["next"] = {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": title,
                    "message": warn_msg,
                    "type": "warning",
                    "sticky": True,
                    "next": {"type": "ir.actions.act_window_close"},
                },
            }
        
        return notification

    @api.depends("move_ids")
    def _compute_mode(self):
        """
        Force mode as 'invoice_multi' for mass sending.
        
        This avoids extra notifications since this module sends
        each invoice individually in the background.
        """
        if not self.env.context.get("account_invoice_mass_sending", False):
            return super()._compute_mode()
        for wizard in self:
            wizard.mode = "invoice_multi"