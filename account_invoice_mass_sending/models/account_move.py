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
        """Send a single invoice using the account.move.send wizard."""
        self.ensure_one()
        
        try:
            # En Odoo 18, usar action_post() si está en draft
            if self.state == 'draft':
                self.action_post()
            
            # Usar action_send_invoice_mail() que es el método estándar de Odoo
            # para enviar la factura por email
            result = self.sudo().action_send_invoice_mail()
            
            # Marcar como completado
            self.write({
                "sending_in_progress": False,
            })
            
            return result
            
        except Exception as e:
            # Si falla, marcar como no en progreso
            self.write({
                "sending_in_progress": False,
            })
            raise