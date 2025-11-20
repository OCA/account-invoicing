# Copyright 2019 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, models


class AccountMoveSendBatchWizard(models.TransientModel):
    """Agregar funcionalidad de envío masivo al wizard batch"""
    
    _inherit = "account.move.send.batch.wizard"

    def enqueue_invoices(self):
        """Enqueue multiple invoices for asynchronous sending."""
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
        
        invoices_to_send = invoices.mass_sending(self.mail_template_id)
        ineligible_invoices = invoices - invoices_to_send
        
        title = _("Invoices: Mass sending")
        msg = _(
            "The sending of %(count)d invoice(s) will be processed in background.",
            count=len(invoices_to_send),
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
        
        if ineligible_invoices:
            invoicelist = [inv.name for inv in ineligible_invoices]
            warn_msg = _(
                "Invoices %(invoices)s were already in processing or do not have an email.",
                invoices=", ".join(invoicelist),
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