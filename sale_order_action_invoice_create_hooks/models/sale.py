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


class SaleOrder(osv.osv):
    _inherit = "sale.order"

    def _selected_invoice_lines(self, cr, uid, order, states, context=None):
        lines = []
        for line in order.order_line:
            if line.invoiced:
                continue
            elif (line.state in states):
                lines.append(line.id)
        return lines

    def action_invoice_create(
            self, cr, uid, ids, grouped=False, states=None,
            date_invoice=False, context=None):
        """ Add HOOK """
        if states is None:
            states = ['confirmed', 'done', 'exception']
        res = False
        invoices = {}
        invoice_ids = []
        invoice = self.pool.get('account.invoice')
        obj_sale_order_line = self.pool.get('sale.order.line')
        partner_currency = {}
        # If date was specified, use it as date invoiced, useful when invoices
        # are generated this month and put the
        # last day of the last month as invoice date
        if date_invoice:
            context = dict(context or {}, date_invoice=date_invoice)
        for o in self.browse(cr, uid, ids, context=context):
            currency_id = o.pricelist_id.currency_id.id
            if (o.partner_id.id in partner_currency) and \
                    (partner_currency[o.partner_id.id] != currency_id):
                raise osv.except_osv(
                    _('Error!'),
                    _('You cannot group sales having different '
                      'currencies for the same partner.'))

            partner_currency[o.partner_id.id] = currency_id
            # HOOK
            lines = self._selected_invoice_lines(cr, uid, o, states, context)
            # --
            # HOOK, add passing context
            created_lines = obj_sale_order_line.invoice_line_create(
                cr, uid, lines, context=context)
            # --
            if created_lines:
                invoices.setdefault(
                    o.partner_invoice_id.id or
                    o.partner_id.id, []).append((o, created_lines))
        if not invoices:
            for o in self.browse(cr, uid, ids, context=context):
                for i in o.invoice_ids:
                    if i.state == 'draft':
                        return i.id
        for val in invoices.values():
            if grouped:
                res = self._make_invoice(cr, uid, val[0][0], reduce(
                    lambda x, y: x + y, [l for o, l in val], []),
                    context=context)
                invoice_ref = ''
                origin_ref = ''
                for o, l in val:
                    invoice_ref += (o.client_order_ref or o.name) + '|'
                    origin_ref += (o.origin or o.name) + '|'
                    self.write(cr, uid, [o.id], {'state': 'progress'})
                    cr.execute(
                        "insert into sale_order_invoice_rel "
                        "(order_id,invoice_id) "
                        "values (%s,%s)", (o.id, res))
                    self.invalidate_cache(
                        cr, uid, ['invoice_ids'], [o.id], context=context)
                # remove last '|' in invoice_ref
                if len(invoice_ref) >= 1:
                    invoice_ref = invoice_ref[:-1]
                if len(origin_ref) >= 1:
                    origin_ref = origin_ref[:-1]
                invoice.write(
                    cr, uid, [res],
                    {'origin': origin_ref, 'name': invoice_ref})
            else:
                for order, il in val:
                    res = self._make_invoice(
                        cr, uid, order, il, context=context)
                    invoice_ids.append(res)
                    self.write(cr, uid, [order.id], {'state': 'progress'})
                    cr.execute(
                        "insert into sale_order_invoice_rel "
                        "(order_id,invoice_id) values (%s,%s)",
                        (order.id, res))
                    self.invalidate_cache(
                        cr, uid, ['invoice_ids'], [order.id], context=context)
        return res
