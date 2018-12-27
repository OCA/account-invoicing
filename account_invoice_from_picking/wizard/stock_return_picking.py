# -*- coding: utf-8 -*-
# Copyright 2018 Akretion
# @author Magno Costa <magno.costa@akretion.com.br>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import api, fields, models, _


class StockReturnPicking(models.TransientModel):
    _inherit = 'stock.return.picking'

    invoice_state = fields.Selection(
        [('2binvoiced', 'To be refunded/invoiced'),
         ('none', 'No invoicing')], 'Invoicing', required=True
    )

    @api.model
    def default_get(self, fields):
        res = super(StockReturnPicking, self).default_get(fields)
        record_id = self.env.context and self.env.context.get(
            'active_id', False) or False
        pick_obj = self.env['stock.picking']
        pick = pick_obj.browse(record_id)
        if pick:
            if 'invoice_state' in fields:
                if pick.invoice_state == 'invoiced':
                    res.update({'invoice_state': '2binvoiced'})
                else:
                    res.update({'invoice_state': 'none'})
        return res

    @api.multi
    def _create_returns(self):
        if self.env.context is None:
            self.env.context = {}
        data = self.browse(self._ids[0])
        new_picking, picking_type_id = super(
            StockReturnPicking, self)._create_returns()
        if data.invoice_state == '2binvoiced':
            pick_obj = self.env["stock.picking"]

            move_ids = [x.id for x in pick_obj.browse(
                new_picking).move_lines]
            for move_id in move_ids:
                move_obj = self.env["stock.move"].browse(move_id)
                move_obj.write({'invoice_state': '2binvoiced'})
        return new_picking, picking_type_id
