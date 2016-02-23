# -*- coding: utf-8 -*-

from openerp.osv import fields, osv


class sale_advance_payment_inv(osv.osv_memory):
    _inherit = "sale.advance.payment.inv"

    def _get_advance_payment_method(self, cr, uid, context=None):
        res = super(
            sale_advance_payment_inv, self)._get_advance_payment_method(
                cr, uid, context=context)
        if context.get('active_model', False) == 'sale.order':
            sale_id = context.get('active_id', False)
            if sale_id:
                sale = self.pool.get('sale.order').browse(cr, uid, sale_id)
                # IF use invoice plan, only 'all' is allowed.
                if sale.use_invoice_plan:
                    res = [('all', 'Invoice the whole sales order')]
        return res

    _columns = {
        'advance_payment_method': fields.selection(
            _get_advance_payment_method,
            'What do you want to invoice?', required=True,
        ),
    }
    _defaults = {
        'advance_payment_method': lambda self, cr, uid, c:
            self._get_advance_payment_method(cr, uid, context=c)[0][0],
    }

sale_advance_payment_inv()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
