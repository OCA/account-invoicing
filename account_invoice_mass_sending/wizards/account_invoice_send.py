# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, models


class AccountInvoiceSend(models.TransientModel):
    _inherit = "account.invoice.send"

    def enqueue_invoices(self):
        active_ids = self._context.get("active_ids")
        invoices = self.env["account.move"].browse(active_ids)
        invoices_to_send = invoices.mass_sending(self.template_id)
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
        if ineligible_invoices:
            invoicelist = [invoice.name for invoice in ineligible_invoices]
            warn_msg = _(
                "Invoices %(ineligible_invoices)s were already in "
                "processing or do not have an email address defined.",
                ineligible_invoices=" ".join(invoicelist),
            )
            notification["params"]["next"].update(
                {
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
            )
        return notification

    @api.onchange("invoice_ids")
    def _compute_composition_mode(self):
        """Force send as mass_mail although this module sends each invoice one by one
        to avoid extra notificactions"""
        if not self.env.context.get("account_invoice_mass_sending", False):
            return super()._compute_composition_mode()
        for wizard in self:
            wizard.composer_id.composition_mode = "mass_mail"
