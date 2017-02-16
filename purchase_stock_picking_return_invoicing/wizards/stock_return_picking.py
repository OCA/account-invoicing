# -*- coding: utf-8 -*-
# Copyright 2017 Eficent Business and IT Consulting Services
#           <contact@eficent.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models


class StockReturnPicking(models.TransientModel):
    _inherit = "stock.return.picking"

    @api.model
    def default_get(self, fields):
        """Get purchase order for lines."""
        result = super(StockReturnPicking, self).default_get(fields)
        try:
            for line in result["product_return_moves"]:
                assert line[0] == 0
                move = self.env["stock.move"].browse(line[2]["move_id"])
                line[2]["purchase_line_id"] = (
                    move.purchase_line_id.id)
        except KeyError:
            pass
        return result

    @api.multi
    def _create_returns(self):
        new_picking_id, pick_type_id = super(
            StockReturnPicking, self)._create_returns()
        new_picking = self.env['stock.picking'].browse(new_picking_id)
        for move in new_picking.move_lines:
            return_picking_line = self.product_return_moves.filtered(
                lambda r: r.move_id == move.origin_returned_move_id)
            if return_picking_line:
                move.purchase_line_id = return_picking_line.purchase_line_id
        return new_picking_id, pick_type_id


class StockReturnPickingLine(models.TransientModel):
    _inherit = "stock.return.picking.line"

    purchase_line_id = fields.Many2one(
        comodel_name='purchase.order.line',
        string="Purchase order line",
        readonly=True)
