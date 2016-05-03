# -*- coding: utf-8 -*-
# © 2016 Apulia Software srl <info@apuliasoftware.it>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, models, _
from openerp.exceptions import Warning as UserError


class AccountInvoice(models.Model):

    _inherit = 'account.invoice'

    @api.model
    def action_number(self):
        res = super(AccountInvoice, self).action_number()
        for invoice in self:
            # ----- Ignore supplier invoice and supplier refund
            if invoice.type in ('in_invoice', 'in_refund'):
                return res
            # ----- Search if exists an invoice, yet
            if self.search([
                    ('type', '=', invoice.type),
                    ('date_invoice', '>', invoice.date_invoice),
                    ('number', '<', invoice.number),
                    ('journal_id', '=', invoice.journal_id.id)], ):
                raise UserError(
                    _('Cannot create invoice!'
                      ' Post the invoice with a greater date'))
        return res
