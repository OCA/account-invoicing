# -*- coding: utf-8 -*-
# Copyright 2017 Eficent Business and IT Consulting Services
#           <contact@eficent.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models
from openerp.tools.float_utils import float_compare


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    @api.depends('order_id.state', 'qty_received', 'qty_invoiced',
                 'product_qty', 'move_ids.state',
                 'invoice_lines.invoice_id.state', 'invoice_lines.quantity')
    def _compute_qty_to_invoice(self):
        for line in self:
            line.qty_to_invoice = line.product_qty - line.qty_invoiced
        precision = self.env['decimal.precision'].precision_get(
            'Product Unit of Measure')
        for line in self:
            line.qty_to_invoice = 0.0
            line.qty_to_refund = 0.0
            if line.order_id.state != 'purchase':
                line.invoice_status = 'no'
                continue
            else:
                if line.product_id.purchase_method == 'receive':
                    qty = (line.qty_received - line.qty_returned) - (
                        line.qty_invoiced - line.qty_refunded)
                    if qty >= 0.0:
                        line.qty_to_invoice = qty
                    else:
                        line.qty_to_refund = abs(qty)
                else:
                    line.qty_to_invoice = line.product_qty - line.qty_invoiced
                    line.qty_to_refund = 0.0

            if line.product_id.purchase_method == 'receive' and not \
                    line.move_ids.filtered(lambda x: x.state == 'done'):
                line.invoice_status = 'to invoice'
                # We would like to put 'no', but that would break standard
                # odoo tests.
                continue

            if abs(float_compare(line.qty_to_invoice, 0.0,
                                 precision_digits=precision)) == 1:
                line.invoice_status = 'to invoice'
            elif abs(float_compare(line.qty_to_refund, 0.0,
                                   precision_digits=precision)) == 1:
                line.invoice_status = 'to invoice'
            elif float_compare(line.qty_to_invoice, 0.0,
                               precision_digits=precision) == 0 \
                    and float_compare(line.qty_to_refund, 0.0,
                                      precision_digits=precision) == 0:
                line.invoice_status = 'invoiced'
            else:
                line.invoice_status = 'no'

    qty_to_invoice = fields.Float(compute="_compute_qty_to_invoice")
