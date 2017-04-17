# -*- coding: utf-8 -*-
# Copyright 2016 Jairo Llopis <jairo.llopis@tecnativa.com>
# Copyright 2017 Sergio Teruel <sergio.teruel@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models


class StockMove(models.Model):
    _inherit = "stock.move"

    to_refund_so = fields.Boolean(
        "To Refund in SO",
        help='Trigger a decrease of the delivered quantity in the associated '
             'Sale Order',
    )
    origin_to_refund_so = fields.Boolean("Origin To Refund in SO")

    @api.multi
    def action_done(self):
        result = super(StockMove, self).action_done()
        # Update returned quantities on sale order lines
        so_lines = self.mapped('procurement_id.sale_line_id').filtered(
            lambda x: x.product_id.invoice_policy in ('order', 'delivery'))
        so_lines._get_qty_returned()
        return result
