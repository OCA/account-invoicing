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
        """Send a single invoice by email directly without using Odoo native methods."""
        self.ensure_one()
        
        try:
            # Publicar factura si está en borrador
            if self.state == 'draft':
                self.action_post()
            
            # Obtener destinatario
            if not self.partner_id.email:
                raise UserError(_("Partner has no email address"))
            
            email_to = self.partner_id.email
            
            # Obtener email remitente
            email_from = self.env.company.email or self.env.user.email
            if not email_from:
                raise UserError(_("No sender email configured"))
            
            # Preparar asunto
            subject = _("Invoice %s") % self.name
            
            # Preparar cuerpo del email (simple)
            body_html = _("""
                <p>Dear %(partner_name)s,</p>
                <p>Please find attached the invoice <strong>%(invoice_name)s</strong>.</p>
                <p>Amount due: %(amount)s</p>
                <br/>
                <p>Best regards,</p>
                <p>%(company_name)s</p>
            """) % {
                'partner_name': self.partner_id.name,
                'invoice_name': self.name,
                'amount': self.amount_total,
                'company_name': self.env.company.name,
            }
            
            # Crear email DIRECTAMENTE sin usar el template estándar
            mail = self.env['mail.mail'].sudo().create({
                'subject': subject,
                'body_html': body_html,
                'email_from': email_from,
                'email_to': email_to,
                'model': 'account.move',
                'res_id': self.id,
            })
            
            # ENVIAR EL EMAIL DIRECTAMENTE
            mail.send()
            
            # Marcar la factura como enviada
            self.sudo().is_move_sent = True
            
            # Crear registro de seguimiento
            self.message_post(
                body=_("Invoice sent by email to %(email)s", email=email_to),
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