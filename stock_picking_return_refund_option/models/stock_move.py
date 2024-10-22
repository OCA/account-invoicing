# Copyright 2021 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import models


class StockMove(models.Model):
    _inherit = "stock.move"

    def write(self, vals):
        res = super().write(vals)
        if "to_refund" in vals:
            for move in self:
                if move.picking_id:
                    move.picking_id.set_delivered_qty()
                    move.picking_id.set_received_qty()
        return res
