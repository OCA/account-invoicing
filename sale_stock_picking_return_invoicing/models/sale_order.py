# -*- coding: utf-8 -*-
# Copyright 2016 Jairo Llopis <jairo.llopis@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.multi
    def _get_delivered_qty(self):
        """Deduct moves marked to refund."""
        qty = super(SaleOrderLine, self)._get_delivered_qty()
        for move in self.procurement_ids.mapped('move_ids').filtered(
                lambda r: (r.state == 'done' and
                           not r.scrapped and
                           r.location_dest_id.usage != "customer" and
                           r.to_refund_so)):
            qty -= move.product_uom._compute_qty_obj(
                move.product_uom, move.product_uom_qty, self.product_uom)
        return qty
