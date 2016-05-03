# -*- coding: utf-8 -*-
# © 2016 Apulia Software srl <info@apuliasoftware.it>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, _
from openerp.exceptions import Warning as UserError


class AccountInvoice(models.Model):

    _inherit = 'account.invoice'

    def action_number(self, cr, uid, ids, context=None):
        res = super(AccountInvoice, self).action_number(
            cr, uid, ids, context=context)
        for invoice in self.browse(cr, uid, ids, context=context):
            # ----- Ignore supplier invoice and supplier refund
            if invoice.type in ('in_invoice', 'in_refund'):
                return res
            # ----- Search if exists an invoice, yet
            if self.search(cr, uid, [
                    ('type', '=', invoice.type),
                    ('date_invoice', '>', invoice.date_invoice),
                    ('number', '<', invoice.number),
                    ('journal_id', '=', invoice.journal_id.id)],
                    context=context):
                raise UserError(
                    _('Cannot create invoice!'
                      ' Post the invoice with a greater date'))
        return res
