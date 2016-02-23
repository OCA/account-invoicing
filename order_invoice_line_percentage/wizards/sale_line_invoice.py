# -*- coding: utf-8 -*-

from openerp.osv import osv


class sale_order_line_make_invoice(osv.osv_memory):

    _inherit = "sale.order.line.make.invoice"

    def _sale_order_line_make_invoice_hook1(self, cr, uid, res, order):
        super(sale_order_line_make_invoice, self).\
            _sale_order_line_make_invoice_hook1(cr, uid, res, order)
        # for Line Percentage invoice, add the advance back.
        inv_obj = self.pool.get('account.invoice')
        invoice = inv_obj.browse(cr, uid, res)
        obj_invoice_line = self.pool.get('account.invoice.line')
        for deposit_inv in order.invoice_ids:
            if deposit_inv.state not in ('cancel',) and \
                    deposit_inv.is_deposit:
                for preline in deposit_inv.invoice_line:
                    ratio = order.amount_untaxed and \
                        (invoice.amount_untaxed /
                         order.amount_untaxed) or 1.0
                    inv_line_id = obj_invoice_line.copy(
                        cr, uid, preline.id,
                        {'invoice_id': res,
                         'price_unit': -preline.price_unit, })
                    inv_line = obj_invoice_line.browse(
                        cr, uid, inv_line_id)
                    obj_invoice_line.write(
                        cr, uid, inv_line_id,
                        {'quantity': inv_line.quantity * ratio})
        # --
        return

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
