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
import logging
from openerp.osv import orm, fields
from openerp import netsvc
from openerp.tools.translate import _


_logger = logging.getLogger(__name__)


class SaleAdvancePaymentInv(orm.TransientModel):
    _inherit = "sale.advance.payment.inv"

    def create_invoices(self, cr, uid, ids, context=None):
        """override standard behavior if payment method is set to 'lines':
        """
        res = super(SaleAdvancePaymentInv, self).create_invoices(
            cr, uid, ids, context)
        wizard = self.browse(cr, uid, ids[0], context)
        if wizard.advance_payment_method != 'lines':
            return res
        sale_ids = context.get('active_ids', [])
        if not sale_ids:
            return res
        wizard_obj = self.pool['sale.order.line.invoice.partially']
        order_line_obj = self.pool['sale.order.line']
        so_domain = [('order_id', 'in', sale_ids), ]
        so_line_ids = order_line_obj.search(
            cr, uid, so_domain, context=context)
        line_values = []
        for so_line in order_line_obj.browse(cr, uid, so_line_ids,
                                             context=context):
            if so_line.state in ('confirmed', 'done') and not so_line.invoiced:
                qty2inv = so_line.product_uom_qty - so_line.qty_invoiced
                val = {'sale_order_line_id': so_line.id,
                       'quantity': qty2inv
                       }
                line_values.append((0, 0, val))
        val = {'line_ids': line_values, }
        wizard_id = wizard_obj.create(cr, uid, val, context=context)
        res = {'view_type': 'form',
               'view_mode': 'form',
               'res_model': 'sale.order.line.invoice.partially',
               'res_id': wizard_id,
               'type': 'ir.actions.act_window',
               'target': 'new',
               'context': context,
               }
        return res


class SaleOrderLineInvoicePartiallyLine(orm.TransientModel):
    _name = "sale.order.line.invoice.partially.line"
    _columns = {
        'wizard_id': fields.many2one('sale.order.line.invoice.partially',
                                     string='Wizard'),
        'sale_order_line_id': fields.many2one('sale.order.line',
                                              string='sale.order.line'),
        'name': fields.related('sale_order_line_id', 'name',
                               type='text', string="Line", readonly=True),
        'order_qty': fields.related('sale_order_line_id', 'product_uom_qty',
                                    type='float', string="Sold",
                                    readonly=True),
        'qty_invoiced': fields.related('sale_order_line_id', 'qty_invoiced',
                                       type='float', string="Invoiced",
                                       readonly=True),
        'quantity': fields.float('To invoice'),
    }

    def _check_to_invoice_qty(self, cr, uid, ids, context=None):
        for record in self.browse(cr, uid, ids, context=context):
            if record.order_qty - record.qty_invoiced < record.quantity:
                return False
        return True

    _constraints = [
        (_check_to_invoice_qty,
         "Quantity to invoice couldn't be greater than remaining quantity",
         ['quantity']),
    ]


class SaleOrderLineInvoicePartially(orm.TransientModel):
    _name = "sale.order.line.invoice.partially"
    _columns = {
        'name': fields.char('Name'),
        'line_ids': fields.one2many('sale.order.line.invoice.partially.line',
                                    'wizard_id', string="Lines"),
    }

    def create_invoice(self, cr, uid, ids, context=None):
        wf_service = netsvc.LocalService('workflow')
        if context is None:
            context = {}
        ctx = context.copy()
        ctx['_partial_invoice'] = {}
        so_line_obj = self.pool['sale.order.line']
        so_obj = self.pool['sale.order']
        order_lines = {}
        invoice_id = False
        for wiz in self.browse(cr, uid, ids, context=context):
            for line in wiz.line_ids:
                if line.quantity == 0:
                    continue
                sale_order = line.sale_order_line_id.order_id
                if sale_order.id not in order_lines:
                    order_lines[sale_order.id] = []
                order_lines[sale_order.id].append(line.sale_order_line_id.id)
                ctx['_partial_invoice'][line.sale_order_line_id.id] = \
                    line.quantity
        for order_id in order_lines:
            so_line_ids = order_lines[order_id]
            invoice_line_ids = so_line_obj.invoice_line_create(
                cr, uid, so_line_ids, context=ctx)
            order = so_obj.browse(cr, uid, order_id, context=context)
            # HACK: Avoid the creation of counterpart lines for compensating
            # false "anticipated" invoice lines (which is the standard
            # behaviour)
            order.invoice_ids = []
            # Call invoice creation
            invoice_id = so_obj._make_invoice(cr, uid, order, invoice_line_ids,
                                              context=ctx)
            _logger.info(_('Created invoice %d'), invoice_id)
            # the following is copied from many places around
            # (actually sale_line_invoice.py)
            cr.execute('INSERT INTO sale_order_invoice_rel (order_id, '
                       '                                    invoice_id) '
                       'VALUES (%s,%s)', (order_id, invoice_id))
            if all(line.invoiced for line in order.order_line):
                wf_service.trg_validate(
                    uid, 'sale.order', order.id, 'manual_invoice', cr)
        # Open invoice
        ir_model_data = self.pool['ir.model.data']
        form_res = ir_model_data.get_object_reference(cr, uid, 'account',
                                                      'invoice_form')
        form_id = form_res and form_res[1] or False
        if invoice_id:
            # Control if no quantities have been selected
            return {
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'account.invoice',
                'res_id': invoice_id,
                'view_id': form_id,
                'context': {'type': 'out_invoice'},
                'type': 'ir.actions.act_window',
            }
        return True
