# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Alexandre Fayolle
#    Copyright 2013 Camptocamp SA
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
"""
 * Adding qty_invoiced field on SO lines, computed based on invoice lines
   linked to it that has the same product. So this way, advance invoice will
   still work !

 * Adding qty_delivered field in SO Lines, computed from move lines linked to
   it. For services, the quantity delivered is a problem, the MRP will
   automatically run the procurement linked to this line and pass it to done. I
   suggest that in that case, delivered qty = invoiced_qty as the procurement
   is for the whole qty, it'll be a good alternative to follow what has been
   done and not.

 * Add in the "Order Line to invoice" view those fields

 * Change the behavior of the "invoiced" field of the SO line to be true when
   all is invoiced

 * Adapt the "_make_invoice" method in SO to deal with qty_invoiced

 * Adapt the sale_line_invoice.py wizard to deal with qty_invoiced, asking the
   user how much he want to invoice.

By having the delivered quantity, we can imagine in the future to provide an
invoicing "based on delivery" that will look at those values instead of looking
in picking.
"""
from openerp.osv import orm, fields
import openerp.addons.decimal_precision as dp


class SaleOrderLine(orm.Model):
    _inherit = 'sale.order.line'

    def field_qty_invoiced(self, cr, uid, ids, field_list, arg, context):
        res = dict.fromkeys(ids, 0)
        precision = self.pool['decimal.precision'].precision_get(
            cr, uid, 'Product UoS')
        for line in self.browse(cr, uid, ids, context=context):
            for invoice_line in line.invoice_lines:
                if invoice_line.invoice_id.state != 'cancel':
                    res[line.id] += invoice_line.quantity  # XXX uom !
            res[line.id] = round(res[line.id], precision)
        return res

    def field_qty_delivered(self, cr, uid, ids, field_list, arg, context):
        res = dict.fromkeys(ids, 0)
        precision = self.pool['decimal.precision'].precision_get(
            cr, uid, 'Product UoS')
        lines = self.browse(cr, uid, ids, context=context)
        for procurement in lines.mapped('procurement_ids'):
            if not procurement.move_ids:
                # consumable or service: assume delivered == invoiced
                res[procurement.sale_line_id.id] = procurement.sale_line_id.qty_invoiced
            else:
                for move in procurement.move_ids:
                    if (move.state == 'done' and
                            move.picking_id and
                            move.picking_type_id.code == 'outgoing'):
                        res[procurement.sale_line_id.id] += move.product_qty
            res[procurement.sale_line_id.id] = round(res[procurement.sale_line_id.id], precision)
        return res

    def _prepare_order_line_invoice_line(self, cr, uid, line, account_id=False,
                                         context=None):
        if context is None:
            context = {}
        res = super(SaleOrderLine, self)._prepare_order_line_invoice_line(
            cr, uid, line, account_id, context=context)
        if '_partial_invoice' in context:
            # we are making a partial invoice for the line
            to_invoice_qty = context['_partial_invoice'][line.id]
        else:
            # we are invoicing the yet uninvoiced part of the line
            to_invoice_qty = line.product_uom_qty - line.qty_invoiced
        res['quantity'] = to_invoice_qty
        return res

    def _fnct_line_invoiced(
            self, cr, uid, ids, field_name, args, context=None
    ):
        res = dict.fromkeys(ids, False)
        for this in self.browse(cr, uid, ids, context=context):
            res[this.id] = (this.qty_invoiced == this.product_uom_qty)
        return res

    def _order_lines_from_invoice2(self, cr, uid, ids, context=None):
        # overridden with different name because called by framework with
        # 'self' an instance of another class
        return self.pool['sale.order.line']._order_lines_from_invoice(
            cr, uid, ids, context)

    _columns = {
        'qty_invoiced': fields.function(
            field_qty_invoiced, string='Invoiced Quantity', type='float',
            digits_compute=dp.get_precision('Product UoS'),
            help="the quantity of product from this line already invoiced"),
        'qty_delivered': fields.function(
            field_qty_delivered, string='Invoiced Quantity', type='float',
            digits_compute=dp.get_precision('Product UoS'),
            help="the quantity of product from this line already invoiced"),
        'invoiced': fields.function(
            _fnct_line_invoiced, string='Invoiced', type='boolean',
            store={
                'account.invoice': (_order_lines_from_invoice2, ['state'], 10),
                'sale.order.line': (lambda self, cr, uid, ids, context=None:
                                    ids, ['invoice_lines'], 10)
            }),
    }

    def search(self, cr, uid, args, offset=0, limit=None, order=None,
            context=None, count=False):
        if '_partial_invoice' in context:
            args.remove(('invoiced', '=', True))
        return super(SaleOrderLine, self).search(cr, uid, args=args, offset=offset, limit=limit, order=order,
            context=context, count=count)

