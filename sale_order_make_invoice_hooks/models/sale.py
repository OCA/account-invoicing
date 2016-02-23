# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Jordi Ballester (Eficent)
#    Copyright 2015 Eficent
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
from openerp.osv import osv
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT
import time


class SaleOrder(osv.osv):
    _inherit = "sale.order"

    def _append_invoice_line(self, cr, uid, invoice, lines, context=None):
        for preline in invoice.invoice_line:
            inv_line_id = self.pool.get('account.invoice.line').\
                copy(cr, uid, preline.id, {'invoice_id': False,
                                           'price_unit': -preline.price_unit})
            lines.append(inv_line_id)
        return lines

    def _make_invoice(self, cr, uid, order, lines, context=None):
        """ Add HOOK """
        inv_obj = self.pool.get('account.invoice')
        # obj_invoice_line = self.pool.get('account.invoice.line')
        if context is None:
            context = {}
        invoiced_sale_line_ids = self.pool.get('sale.order.line').search(
            cr, uid, [('order_id', '=', order.id), ('invoiced', '=', True)],
            context=context)
        from_line_invoice_ids = []
        for invoiced_sale_line_id in self.pool.get('sale.order.line').browse(
                cr, uid, invoiced_sale_line_ids, context=context):
            for invoice_line_id in invoiced_sale_line_id.invoice_lines:
                if invoice_line_id.invoice_id.id not in from_line_invoice_ids:
                    from_line_invoice_ids.append(invoice_line_id.invoice_id.id)
        for preinv in order.invoice_ids:
            if preinv.state not in ('cancel',) and \
                    preinv.id not in from_line_invoice_ids:
                # HOOK
                lines = self._append_invoice_line(cr, uid,
                                                  preinv, lines,
                                                  context=context)
                # --
        inv = self._prepare_invoice(cr, uid, order, lines, context=context)
        inv_id = inv_obj.create(cr, uid, inv, context=context)
        # HOOK
        date_invoice = context.get('date_invoice', False) or \
            time.strftime(DEFAULT_SERVER_DATE_FORMAT)
        data = inv_obj.onchange_payment_term_date_invoice(cr, uid, [inv_id],
                                                          inv['payment_term'],
                                                          date_invoice)
        # --
        if data.get('value', False):
            inv_obj.write(cr, uid, [inv_id], data['value'], context=context)
        inv_obj.button_compute(cr, uid, [inv_id])
        return inv_id
