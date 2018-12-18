# Copyright 2018 Eficent Business and IT Consulting Services, S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models
from odoo.addons.account.models.account_payment import \
    MAP_INVOICE_TYPE_PARTNER_TYPE


class AccountRegisterPayments(models.TransientModel):
    _inherit = "account.register.payments"

    @api.model
    def default_get(self, fields):
        rec = super(AccountRegisterPayments, self).default_get(fields)
        active_ids = self._context.get('active_ids')
        invoices = self.env['account.invoice'].browse(active_ids)

        # Look if we are mixin multiple alternate_payer or
        # customer invoices with vendor bills
        payer = invoices[0].alternate_payer_id or \
            invoices[0].commercial_partner_id
        multi = any(inv.alternate_payer_id or inv.commercial_partner_id !=
                    payer for inv in invoices)
        payer_id = invoices[0].alternate_payer_id.id or \
            invoices[0].commercial_partner_id.id
        rec['partner_id'] = False if multi else payer_id
        rec['multi'] = multi
        return rec

    @api.multi
    def _groupby_invoices(self):
        # We have to re-group because the old groups are not valid anymore
        super(AccountRegisterPayments, self)._groupby_invoices()
        results = {}
        for inv in self.invoice_ids:
            payer = inv.alternate_payer_id.id or inv.commercial_partner_id.id
            key = (payer, MAP_INVOICE_TYPE_PARTNER_TYPE[inv.type])
            if key not in results:
                results[key] = self.env['account.invoice']
            results[key] += inv
        return results

    @api.multi
    def _prepare_payment_vals(self, invoices):
        res = super(AccountRegisterPayments, self)._prepare_payment_vals(
            invoices)
        payer_id = invoices[0].alternate_payer_id.id or \
            invoices[0].commercial_partner_id.id
        res['partner_id'] = payer_id
        return res
