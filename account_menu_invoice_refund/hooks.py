# Copyright 2019 Ecosoft Co., Ltd (http://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import api, _
from odoo.exceptions import UserError
from odoo.addons.account.models.account_payment import account_abstract_payment

MAP_INVOICE_TYPE_PARTNER_TYPE = {
    'out_invoice': 'customer',
    'out_refund': 'customer',
    'in_invoice': 'supplier',
    'in_refund': 'supplier',
}


def post_load_hook():

    @api.model
    def new_default_get(self, fields):
        """ Removed condition that disallow mixing invoice and refund """
        rec = super(account_abstract_payment, self).default_get(fields)
        active_ids = self._context.get('active_ids')
        active_model = self._context.get('active_model')

        # Check for selected invoices ids
        if not active_ids or active_model != 'account.invoice':
            return rec

        invoices = self.env['account.invoice'].browse(active_ids)

        # Check all invoices are open
        if any(invoice.state != 'open' for invoice in invoices):
            raise UserError(
                _("You can only register payments for open invoices"))
        # Check all invoices have the same currency
        if any(inv.currency_id != invoices[0].currency_id for inv in invoices):
            raise UserError(_("In order to pay multiple invoices "
                              "at once, they must use the same currency."))

        # Look if we are mixin multiple commercial_partner
        # or customer invoices with vendor bills
        multi = any(inv.commercial_partner_id !=
                    invoices[0].commercial_partner_id
                    or MAP_INVOICE_TYPE_PARTNER_TYPE[inv.type] !=
                    MAP_INVOICE_TYPE_PARTNER_TYPE[invoices[0].type]
                    or inv.account_id != invoices[0].account_id
                    or inv.partner_bank_id != invoices[0].partner_bank_id
                    for inv in invoices)

        currency = invoices[0].currency_id

        total_amount = self._compute_payment_amount(invoices=invoices,
                                                    currency=currency)

        rec.update({
            'amount': abs(total_amount),
            'currency_id': currency.id,
            'payment_type': total_amount > 0 and 'inbound' or 'outbound',
            'partner_id': (False if multi else
                           invoices[0].commercial_partner_id.id),
            'partner_type': (False if multi else
                             MAP_INVOICE_TYPE_PARTNER_TYPE[invoices[0].type]),
            'communication': ' '.join(
                [ref for ref in invoices.mapped('reference') if ref])[:2000],
            'invoice_ids': [(6, 0, invoices.ids)],
            'multi': multi,
        })
        return rec

    if not hasattr(account_abstract_payment,
                   'default_get_original'):
        account_abstract_payment.default_get_original = \
            account_abstract_payment.default_get

    account_abstract_payment.default_get = new_default_get
