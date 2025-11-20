# Copyright 2019 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, models


class AccountMoveSendWizard(models.TransientModel):
    """Agregar funcionalidad de envío masivo al wizard individual"""
    
    _inherit = "account.move.send.wizard"

    def enqueue_invoices(self):
        """Enqueue single invoice for asynchronous sending."""
        invoices = self.env["account.move"].browse(
            self.env.context.get("active_ids", [])
        )
        
        if not invoices:
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
        
        # En wizard individual, siempre hay mail_template_id
        mail_template = self.mail_template_id
        
        if not mail_template:
            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": _("Error"),
                    "message": _("No email template selected."),
                    "type": "danger",
                    "next": {"type": "ir.actions.act_window_close"},
                },
            }
        
        # Llamar al método mass_sending del modelo account.move
        invoices_to_send = invoices.mass_sending(mail_template)
        
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": _("Invoices: Mass sending"),
                "message": _(
                    "The sending of %(count)d invoice(s) will be processed in background.",
                    count=len(invoices_to_send),
                ),
                "type": "success",
                "next": {"type": "ir.actions.act_window_close"},
            },
        }