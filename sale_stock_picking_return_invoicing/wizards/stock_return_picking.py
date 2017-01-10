# -*- coding: utf-8 -*-
# Copyright 2016 Jairo Llopis <jairo.llopis@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models

import logging
_logger = logging.getLogger(__name__)

class StockReturnPicking(models.TransientModel):
    _inherit = "stock.return.picking"

    @api.model
    def default_get(self, fields):
        """Get sale order for lines."""
        result = super(StockReturnPicking, self).default_get(fields)
        try:
            for line in result["product_return_moves"]:
                assert line[0] == 0
                move = self.env["stock.move"].browse(line[2]["move_id"])
                line[2]["sale_order_id"] = (move.procurement_id.sale_line_id
                                            .order_id.id)
                line[2]["purchase_order_id"] = (move.purchase_line_id
                                            .order_id.id)
        except KeyError:
            pass
        return result

    @api.multi
    def _create_returns(self):
        """Mark lines to refund."""
        new_picking_id, pick_type_id = super(
            StockReturnPicking, self)._create_returns()
        new_picking = self.env['stock.picking'].browse(new_picking_id)
        
        for move in new_picking.move_lines:
            return_picking_line = self.product_return_moves.filtered(
                lambda r: r.move_id == move.origin_returned_move_id)
            if return_picking_line and return_picking_line.to_refund_so:
                move.to_refund_so = True
            # Add this new move to the purchase line
            if return_picking_line.purchase_order_id:
                move.purchase_line_id = return_picking_line.move_id.purchase_line_id
        return new_picking_id, pick_type_id


class StockReturnPickingLine(models.TransientModel):
    _inherit = "stock.return.picking.line"

    to_refund_so = fields.Boolean(
        string="To Refund",
        help='Trigger a decrease of the delivered quantity in the associated '
             'Sale Order',
    )
    # HACK https://github.com/odoo/odoo/issues/13974
    # We use this to know if we should display `to_refund_so`, and let the job
    # for another addon to implement `to_refund_po`.
    # Cannot use a related field because default_get is patched in main model.
    sale_order_id = fields.Many2one(
        comodel_name="sale.order",
        string="Sale order",
        ondelete="cascade",
        readonly=True,
    )
    purchase_order_id = fields.Many2one(
        comodel_name="purchase.order",
        string="Purchase order",
        ondelete="cascade",
        readonly=True,
    )