# -*- coding: utf-8 -*-
# (c) 2015 Alex Comba - Agile Business Group
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import models, api


class StockMove(models.Model):
    _inherit = 'stock.move'

    @api.multi
    def action_confirm(self):
        """
            Pass the incoterm to the picking from the sales order
        """
        procs_to_check = []
        for move in self:
            if move.procurement_id.sale_line_id.order_id.incoterm:
                procs_to_check += [move.procurement_id]
        res = super(StockMove, self).action_confirm()
        for proc in procs_to_check:
            pickings = proc.mapped('move_ids.picking_id')
            pickings.write(
                {'incoterm': proc.sale_line_id.order_id.incoterm.id})
        return res
