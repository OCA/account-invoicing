# -*- coding: utf-8 -*-
# Copyright 2017 Sergio Teruel <sergio.teruel@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    to_refund_lines = fields.Selection(selection=[
        ('keep_line_value', 'Keep Line Value'),
        ('to_refund_so', 'To Refund In Sales Order'),
        ('no_refund_so', 'No Refund In Sales Order')],
        string='Refund Options', default='keep_line_value',
        help="This field allow modify 'to_refund_so' field value in all "
             "stock moves from this picking after it has been confirmed."
             "keep_line_value: keep the original value.\n"
             "to_refund_so: set all stock moves to True value and recompute "
             "delivered quantities in sale order.\n"
             "no_refund_so: set all stock moves to False value and recompute "
             "delivered quantities in sale order.",
    )

    @api.multi
    def _update_stock_moves(self):
        for pick in self:
            for move in pick.move_lines:
                if pick.to_refund_lines == 'keep_line_value':
                    move.to_refund_so = move.origin_to_refund_so
                elif pick.to_refund_lines == 'to_refund_so':
                    move.to_refund_so = True
                elif pick.to_refund_lines == 'no_refund_so':
                    move.to_refund_so = False

    @api.multi
    def set_delivered_qty(self):
        so_lines = self.mapped(
            'move_lines.procurement_id.sale_line_id').filtered(
            lambda x: x.product_id.invoice_policy in ('order', 'delivery'))
        for so_line in so_lines:
            so_line.qty_delivered = so_line._get_delivered_qty()
            so_line._get_qty_returned()

    @api.multi
    def write(self, vals):
        res = super(StockPicking, self).write(vals)
        if 'to_refund_lines' in vals:
            for picking in self:
                picking._update_stock_moves()
                picking.set_delivered_qty()
        return res
