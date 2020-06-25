# Copyright 2020 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class AccountInvoiceSend(models.TransientModel):

    _inherit = 'account.invoice.send'

    is_transmit = fields.Boolean(
        'Transmit',
        default=lambda self: self.env.user.company_id.invoice_is_transmit
    )

    def _transmit_invoices(self):
        if not self.is_transmit:
            return
        for invoice in self.invoice_ids:
            transmitted = invoice._transmit_invoice()
            if self.env.context.get('mark_invoice_as_sent') and transmitted:
                invoice.write({'sent': True})

    def send_and_print_action(self):
        res = super().send_and_print_action()
        self._transmit_invoices()
        return res
