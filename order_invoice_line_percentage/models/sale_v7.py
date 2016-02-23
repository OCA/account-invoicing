# -*- coding: utf-8 -*-

from openerp.osv import fields, osv


class sale_order(osv.osv):

    _inherit = 'sale.order'

    def _invoiced_rate(self, cursor, user, ids, name, arg, context=None):
        """ Overwrite (ok) """
        res = {}
        for sale in self.browse(cursor, user, ids, context=context):
            if sale.invoiced:
                res[sale.id] = 100.0
                continue
            tot = 0.0
            tot_deposit = 0.0
            tot_non_deposit = 0.0
            for invoice in sale.invoice_ids:
                if invoice.state not in ('cancel') and not invoice.is_deposit:
                    # Assume negative line amount to be Advance deduction
                    for line in invoice.invoice_line:
                        tot_non_deposit += line.price_subtotal > 0.0 and \
                            line.price_subtotal or 0.0
            tot = tot_deposit + tot_non_deposit
            if tot:
                res[sale.id] = min(
                    100.0, tot * 100.0 / (sale.amount_untaxed or 1.00))
            else:
                res[sale.id] = 0.0
        return res

    _columns = {
        'invoiced_rate': fields.function(
            _invoiced_rate, string='Invoiced Ratio', type='float'),
    }


class sale_order_line(osv.osv):

    _inherit = 'sale.order.line'

    # A complete overwrite (ok) method of sale_order_line
    def _fnct_line_invoiced(
            self, cr, uid, ids, field_name, args, context=None):
        res = dict.fromkeys(ids, False)
        uom_obj = self.pool.get('product.uom')
        for this in self.browse(cr, uid, ids, context=context):
            # kittiu, if product line, we need to calculate carefully
            # TODO: uos case is not covered yet.
            if this.product_id and not this.product_uos:
                oline_qty = uom_obj._compute_qty(
                    cr, uid, this.product_uom.id, this.product_uom_qty,
                    this.product_id.uom_id.id, round=False)
                iline_qty = 0.0
                for iline in this.invoice_lines:
                    if iline.invoice_id.state != 'cancel':
                        if not this.product_uos:  # Normal Case
                            iline_qty += uom_obj._compute_qty(
                                cr, uid, iline.uos_id.id, iline.quantity,
                                iline.product_id and
                                iline.product_id.uom_id.id or False,
                                round=False)
                        else:  # UOS case.
                            iline_qty += iline.quantity / \
                                (iline.product_id.uos_id and
                                 iline.product_id.uos_coeff or 1)
                # Test quantity
                res[this.id] = iline_qty >= oline_qty
            else:
                res[this.id] = this.invoice_lines and \
                    all(iline.invoice_id.state !=
                        'cancel' for iline in this.invoice_lines)
        return res

    # A complete overwrite method. We need it here because it is called from a
    # function field.
    def _order_lines_from_invoice(self, cr, uid, ids, context=None):
        # direct access to the m2m table is the less convoluted way to achieve
        # this (and is ok ACL-wise)
        cr.execute("""SELECT DISTINCT sol.id FROM sale_order_invoice_rel rel JOIN
            sale_order_line sol ON (sol.order_id = rel.order_id)
            WHERE rel.invoice_id = ANY(%s)""", (list(ids),))
        return [i[0] for i in cr.fetchall()]

    def _prepare_order_line_invoice_line(
            self, cr, uid, line, account_id=False, context=None):
        res = super(sale_order_line, self)._prepare_order_line_invoice_line(
            cr, uid, line, account_id=account_id, context=context)
        line_percent = context.get('line_percent', False)
        if line_percent:
            res.update(
                {'quantity':
                 (res.get('quantity') or 0.0) * (line_percent / 100)})
        return res

    _columns = {
        'invoiced': fields.function(
            _fnct_line_invoiced, string='Invoiced', type='boolean',
            store={
                'account.invoice': (_order_lines_from_invoice, ['state'], 10),
                'sale.order.line': (lambda self, cr, uid, ids, ctx=None: ids,
                                    ['invoice_lines'], 10)}),
    }

sale_order_line()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
