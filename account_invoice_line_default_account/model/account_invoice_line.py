# -*- coding: UTF-8 -*-
'''
Created on 30 jan. 2013

@author: Ronald Portier, Therp

rportier@therp.nl
http://www.therp.nl
'''
from openerp.osv import orm


class account_invoice_line(orm.Model):
    _inherit = 'account.invoice.line'
    
    def _account_id_default(self, cr, uid, context=None):
        if context is None:
            context = {}
        partner_id = context.get('partner_id', 0)
        invoice_type = context.get('type')
        if (partner_id and invoice_type
        and invoice_type in ['in_invoice', 'in_refund']):
            partner_model = self.pool.get('res.partner')
            partner_obj = partner_model.browse(
                cr, uid, context['partner_id'], context=context)
            if  partner_obj and partner_obj['property_account_expense']:
                return partner_obj.property_account_expense.id
        return False

    _defaults = {
        'account_id': _account_id_default,
    }
    
    def onchange_account_id(
            self, cr, uid, ids, product_id, partner_id, inv_type,
            fposition_id, account_id):
        if (account_id and partner_id and (not product_id)
        and inv_type in ['in_invoice', 'in_refund']):
            # We have an account_id, and is not from a product, so
            # store it in partner automagically:
            partner_model = self.pool.get('res.partner')
            partner_obj = partner_model.browse(cr, uid, partner_id)
            if  partner_obj and partner_obj.auto_update_account_expense:
                old_account_id = (
                    (partner_obj['property_account_expense']
                     and partner_obj.property_account_expense.id) or 0)
                if  not account_id == old_account_id:
                    # only write when something really changed
                    vals = {'property_account_expense': account_id}
                    partner_obj.write(vals)
        return super(account_invoice_line, self).onchange_account_id(
                cr, uid, ids, product_id, partner_id, inv_type,
                fposition_id, account_id)
