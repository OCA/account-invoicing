# -*- coding: utf-8 -*-
# (c) 2015 Alex Comba - Agile Business Group
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import models, api


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    @api.model
    def _invoice_create_line(self, moves, journal_id, inv_type='out_invoice'):
        invoice_id = super(StockPicking, self)._invoice_create_line(
            moves, journal_id, inv_type=inv_type)
        related_picking_ids = {}
        for move in moves:
            if (move.picking_id
                    and move.picking_id.id not in related_picking_ids):
                related_picking_ids[move.picking_id.id] = move
        if invoice_id and related_picking_ids:
            invoice = self.env['account.invoice'].browse(invoice_id)
            invoice.related_picking_ids = [(6, 0, related_picking_ids.keys())]
        return invoice_id
