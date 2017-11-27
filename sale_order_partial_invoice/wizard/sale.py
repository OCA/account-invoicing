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
from openerp import models, fields, api
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp

_logger = logging.getLogger(__name__)


class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = "sale.advance.payment.inv"

    @api.multi
    def create_invoices(self):
        """override standard behavior if payment method is set to 'lines':
        """
        res = super(SaleAdvancePaymentInv, self).create_invoices()
        if self.advance_payment_method != 'lines':
            return res
        sale_ids = self._context.get('active_ids', [])
        if not sale_ids:
            return res
        wizard_obj = self.env['sale.order.line.invoice.partially']
        order_line_obj = self.env['sale.order.line']
        so_domain = [('order_id', 'in', sale_ids), ]
        so_lines = order_line_obj.search(so_domain)
        line_values = []
        for so_line in so_lines:
            if so_line.state in ('confirmed', 'done') and not so_line.invoiced:
                val = {'sale_order_line_id': so_line.id, }
                if so_line.product_id and so_line.product_id.type == 'product':
                    val['quantity'] = so_line.qty_delivered - \
                                      so_line.qty_invoiced
                else:
                    # service or consumable
                    val['quantity'] = so_line.product_uom_qty - \
                                      so_line.qty_invoiced
                line_values.append((0, 0, val))
        val = {'line_ids': line_values, }
        wizard = wizard_obj.create(val)
        res = {'view_type': 'form',
               'view_mode': 'form',
               'res_model': 'sale.order.line.invoice.partially',
               'res_id': wizard.id,
               'type': 'ir.actions.act_window',
               'target': 'new',
               'context': self._context,
               }
        return res


class SaleOrderLineInvoicePartiallyLine(models.TransientModel):
    _name = "sale.order.line.invoice.partially.line"

    wizard_id = fields.Many2one(
        'sale.order.line.invoice.partially',
        string='Wizard')
    sale_order_line_id = fields.Many2one(
        'sale.order.line',
        string='sale.order.line')
    name = fields.Text(
        related='sale_order_line_id.name',
        string="Line",
        readonly=True)
    order_qty = fields.Float(
        related='sale_order_line_id.product_uom_qty',
        string="Sold",
        readonly=True)
    qty_invoiced = fields.Float(
        related='sale_order_line_id.qty_invoiced',
        type='float', string="Invoiced",
        readonly=True)
    qty_delivered = fields.Float(
        related='sale_order_line_id.qty_delivered',
        string="Shipped",
        readonly=True)
    quantity = fields.Float(
        digits=dp.get_precision("Product UoS"),
        string='To invoice')

    @api.one
    @api.constrains('quantity')
    def _check_to_invoice_qty(self):
        precision = self.env['decimal.precision'].precision_get("Product UoS")
        if round(self.order_qty - self.qty_invoiced, precision) < round(
                self.quantity, precision):
            raise Warning(
                _("Quantity to invoice couldn't be "
                  "greater than remaining quantity"))


class SaleOrderLineInvoicePartially(models.TransientModel):
    _name = "sale.order.line.invoice.partially"

    name = fields.Char(string='Name')
    line_ids = fields.One2many(
        'sale.order.line.invoice.partially.line',
        'wizard_id', string="Lines")

    @api.multi
    def create_invoice(self):
        partial_invoice = {}
        so_line_obj = self.env['sale.order.line']
        so_obj = self.env['sale.order']
        order_lines = {}
        invoice_id = False
        for wiz in self:
            for line in wiz.line_ids:
                if line.quantity == 0:
                    continue
                sale_order = line.sale_order_line_id.order_id
                if sale_order.id not in order_lines:
                    order_lines[sale_order.id] = []
                order_lines[sale_order.id].append(line.sale_order_line_id.id)
                partial_invoice[line.sale_order_line_id.id] = \
                    line.quantity
        for order_id in order_lines:
            so_lines = so_line_obj.browse(order_lines[order_id])
            invoice_line_ids = so_lines.with_context(
                _partial_invoice=partial_invoice).invoice_line_create()
            order = so_obj.browse(order_id)
            # HACK: Avoid the creation of counterpart lines for compensating
            # false "anticipated" invoice lines (which is the standard
            # behaviour)
            order.invoice_ids = []
            # Call invoice creation
            invoice_id = so_obj.with_context(
                _partial_invoice=partial_invoice)._make_invoice(
                order, invoice_line_ids)
            _logger.info(_('Created invoice %d'), invoice_id)
            # the following is copied from many places around
            # (actually sale_line_invoice.py)
            self._cr.execute('INSERT INTO sale_order_invoice_rel (order_id, '
                             '                                    invoice_id) '
                             'VALUES (%s,%s)', (order_id, invoice_id))
            if all(line.invoiced for line in order.order_line):
                order.signal_workflow('manual_invoice')
        # Open invoice
        form_res = self.env.ref('account.invoice_form')
        if invoice_id:
            # Control if no quantities have been selected
            return {
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'account.invoice',
                'res_id': invoice_id,
                'view_id': form_res.id,
                'context': {'type': 'out_invoice'},
                'type': 'ir.actions.act_window',
            }
        return True
