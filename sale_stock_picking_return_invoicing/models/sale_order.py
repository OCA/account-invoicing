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
            lambda r: (
                r.state == 'done' and
                not r.scrapped and
                r.to_refund_so))
        qty_to_refund = sum(moves.mapped('quant_ids').filtered(
            lambda x: x.location_id.usage == 'internal').mapped('qty'))
        return qty - qty_to_refund

    @api.multi
    def _get_qty_returned(self):
        """Computes the returned quantity on sale order lines, based on quants
         of done stock moves related to its procurements
        """
        for line in self:
            quants = line.procurement_ids.mapped('move_ids').filtered(
                lambda r: r.state == 'done').mapped('quant_ids')
            qty_returned = sum(quants.filtered(
                lambda x: x.location_id.usage == 'internal').mapped('qty'))
            line.qty_returned = qty_returned

    qty_returned = fields.Float(
        string='Returned Qty',
        digits=dp.get_precision('Product Unit of Measure'),
        copy=False,
    )
