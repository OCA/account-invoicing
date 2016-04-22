# -*- coding: utf-8 -*-
# © 2016 Apulia Software srl <info@apuliasoftware.it> 
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, _
from openerp.exceptions import Warning as UserError

class account_invoice(models.Model):

    _inherit = 'account.invoice'

    def action_number(self, cr, uid, ids, context=None):
        res = super(account_invoice, self).action_number(cr, uid, ids, context=context)
        for obj_inv in self.browse(cr, uid, ids, context=context):
            inv_type = obj_inv.type
            if inv_type == 'in_invoice' or inv_type == 'in_refund':
                return True
            number = obj_inv.number
            date_invoice = obj_inv.date_invoice
            journal = obj_inv.journal_id.id
            res = self.search(
                cr, uid, [
                    ('type','=',inv_type),
                    ('date_invoice','>',date_invoice),
                    ('number', '<', number),
                    ('journal_id','=',journal)],
                context=context)
            if res:
                raise UserError(
                    _('Cannot create invoice! Post the invoice with a greater date'))
        return res

