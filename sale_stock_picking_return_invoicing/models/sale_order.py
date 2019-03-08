# -*- coding: utf-8 -*-
# Copyright 2016 Jairo Llopis <jairo.llopis@tecnativa.com>
# Copyright 2017 Sergio Teruel <sergio.teruel@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models
import openerp.addons.decimal_precision as dp


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.multi
    def _get_delivered_qty(self):
        """Deduct moves marked to refund."""
        qty = super(SaleOrderLine, self)._get_delivered_qty()
        moves = self.procurement_ids.mapped('move_ids').filtered(
            lambda r: r.state == 'done' and not r.scrapped)
        # sum quantities in customers from re-returned pickings.
        # Odoo does not consider them
        for move in moves.filtered(lambda r: (
                r.location_dest_id.usage == "customer" and
                r.origin_returned_move_id)):
            qty += self.env['product.uom']._compute_qty_obj(
                move.product_uom, move.product_uom_qty, self.product_uom)

        for move in moves.filtered(
                lambda r: (r.location_dest_id.usage != "customer" and
                           r.to_refund_so and
                           r.origin_returned_move_id)):
            qty -= move.product_uom._compute_qty_obj(
                move.product_uom, move.product_uom_qty, self.product_uom)
        return qty

    @api.multi
    def _get_qty_returned(self):
        """Computes the returned quantity on sale order lines, based on quants
         of done stock moves related to its procurements
        """
        for line in self:
            qty_returned = 0.0
            for move in line.procurement_ids.mapped('move_ids').filtered(
                    lambda r: (r.state == 'done' and not r.scrapped and
                               r.location_dest_id.usage != "customer" and
                               r.to_refund_so and
                               r.origin_returned_move_id)
            ):
                qty_returned += move.product_uom._compute_qty_obj(
                    move.product_uom, move.product_uom_qty, line.product_uom)
            line.qty_returned = qty_returned

    qty_returned = fields.Float(
        string='Returned Qty',
        digits=dp.get_precision('Product Unit of Measure'),
        copy=False,
    )
