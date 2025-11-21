# Copyright 2019 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import UserError


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
        """Send a single invoice directly without batch mode."""
        self.ensure_one()
        
        try:
            # Publicar factura si está en borrador
            if self.state == 'draft':
                self.action_post()
            
            # USAR action_send_invoice_mail() directamente
            # Esto envía SOLO la factura, sin batch mode
            self.sudo().action_send_invoice_mail()
            
            # Marcar la factura como enviada para limpiar el estado
            # "Esta factura se envía en segundo plano"
            self.sudo().message_post(
                body=_("Invoice sent by email to %(email)s", email=self.partner_id.email),
                message_type='notification',
            )
            
            # Marcar como completado
            self.write({
                "sending_in_progress": False,
            })
            
            return True
            
        except Exception as e:
            # Si falla, marcar como no en progreso y registrar el error
            self.write({
                "sending_in_progress": False,
            })
            
            # Registrar el error en el seguimiento
            self.message_post(
                body=_("Error sending invoice by email: %(error)s", error=str(e)),
                message_type='notification',
                subtype_xmlid='mail.mt_comment',
            )
            
            raise