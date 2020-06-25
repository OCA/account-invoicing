# © 2017 Akretion (http://www.akretion.com)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields
from odoo.tests.common import Form


class TransmitMethod(models.Model):
    _name = 'transmit.method'
    _description = 'Transmit Method of a document'

    name = fields.Char(string='Name', required=True)
    code = fields.Char(
        string='Code', copy=False,
        help="Do not modify the code of an existing Transmit Method "
        "because it may be used to identify a particular transmit method.")
    customer_ok = fields.Boolean(
        string='Selectable on Customers', default=True)
    supplier_ok = fields.Boolean(
        string='Selectable on Vendors', default=True)
    send_mail = fields.Boolean()
    mail_template_id = fields.Many2one(
        'mail.template',
        domain="[('model', '=', 'account.invoice')]"
    )

    _sql_constraints = [(
        'code_unique',
        'unique(code)',
        'This transmit method code already exists!'
    )]

    def _update_send_mail_composer(self, invoice, composer_form):
        # We create this as a hook if someone wants to add encryption,
        # extra attachments or other stuff
        pass

    def _transmit_send_invoice(self, invoice):
        action = invoice.action_invoice_sent()
        template = self.mail_template_id.id or action['context']['default_template_id']
        # We need to put the new template if existent
        action['context'].update({
            'default_use_template': bool(template),
            'default_template_id': template or False,
            'default_is_email': True,
        })
        with Form(
            self.env[action['res_model']].with_context(**action['context'])
        ) as composer_form:
            self._update_send_mail_composer(invoice, composer_form)
            composer = composer_form.save()
            composer._send_email()
        return True

    def _transmit_invoice(self, invoice):
        if self.send_mail:
            return self._transmit_send_invoice(invoice)
        # If no configuration is made, no integration needs to be done.
        return False
