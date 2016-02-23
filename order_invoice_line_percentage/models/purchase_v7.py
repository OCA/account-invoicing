# -*- coding: utf-8 -*-

from openerp.osv import fields, osv


class purchase_order(osv.osv):

    _inherit = 'purchase.order'

    _columns = {
        'invoice_method': fields.selection(
            [('manual', 'Based on Purchase Order lines'),
             ('order', 'Based on generated draft invoice'),
             ('picking', 'Based on incoming shipments'),
             ('line_percentage', 'Based on line percentage')],
            'Invoicing Control', required=True,
            readonly=True,
            states={'draft': [('readonly', False)],
                    'sent': [('readonly', False)]},
            help="Based on Purchase Order lines: place individual lines in "
            "'Invoice Control > Based on P.O. lines' from "
            "where you can selectively create an invoice.\n"
            "Based on generated invoice: create a draft invoice you "
            "can validate later.\n"
            "Based on incoming shipments: let you create an invoice when "
            "receptions are validated.\n"
            "Based on line percentage: let you enter percentage of all "
            "invoice lines"
        ),
    }

    def _prepare_inv_line(self, cr, uid, account_id, order_line, context=None):
        if context is None:
            context = {}
        res = super(purchase_order, self)._prepare_inv_line(
            cr, uid, account_id, order_line, context=context)
        line_percent = context.get('line_percent', False)
        if line_percent:
            res.update(
                {'quantity':
                 (res.get('quantity') or 0.0) * (line_percent / 100)})
        return res

purchase_order()


class purchase_order_line(osv.osv):

    _inherit = 'purchase.order.line'

    def _fnct_line_invoiced(
            self, cr, uid, ids,
            field_name, args, context=None):
        res = dict.fromkeys(ids, False)
        uom_obj = self.pool.get('product.uom')
        for this in self.browse(cr, uid, ids, context=context):
            if this.product_id:
                oline_qty = uom_obj._compute_qty(
                    cr, uid, this.product_uom.id,
                    this.product_qty, this.product_id.uom_id.id)
                iline_qty = 0.0
                for iline in this.invoice_lines:
                    if iline.invoice_id.state != 'cancel':
                        iline_qty += uom_obj._compute_qty(
                            cr, uid, iline.uos_id.id, iline.quantity,
                            iline.product_id and iline.product_id.uom_id.id or
                            False)
                # Test quantity
                res[this.id] = iline_qty >= oline_qty
            else:
                res[this.id] = this.invoice_lines and \
                    all(iline.invoice_id.state != 'cancel'
                        for iline in this.invoice_lines)
        return res

    def _order_lines_from_invoice(self, cr, uid, ids, context=None):
        # direct access to the m2m table is the less convoluted way to achieve
        # this (and is ok ACL-wise)
        cr.execute("""SELECT DISTINCT pol.id FROM purchase_invoice_rel rel JOIN
            purchase_order_line pol ON (pol.order_id = rel.purchase_id)
            WHERE rel.invoice_id = ANY(%s)""", (list(ids),))
        res = [i[0] for i in cr.fetchall()]
        return res

    _columns = {
        'invoiced': fields.function(
            _fnct_line_invoiced, string='Invoiced', type='boolean',
            store={
                'account.invoice': (_order_lines_from_invoice, ['state'], 10),
                'purchase.order.line': (lambda self, cr, uid, ids, ctx=None:
                                        ids, ['invoice_lines'], 10)}),
    }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
