# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from collections import defaultdict

from odoo import api, fields, models


class StockMove(models.Model):
    _inherit = "stock.move"

    charge_restocking_fee = fields.Boolean(
        help="If checked your customer will be charged for accepting "
             "returned goods.",
        default=False,
        readonly=True,
    )
    is_customer_return = fields.Boolean(
        related="picking_id.is_customer_return", readonly=True
    )

    @api.multi
    def action_done(self):
        result = super(StockMove, self).action_done()
        move_ids_to_charge_by_so = defaultdict(list)
        for move in self:
            if not move._is_restocking_fee_chargeable():
                continue
            so = move.procurement_id.sale_line_id.order_id
            move_ids_to_charge_by_so[so].append(move.id)
        for so, move_ids_to_charge in move_ids_to_charge_by_so.items():
            so._charge_restocking_fee(
                self.browse(move_ids_to_charge)
            )
        return result

    @api.multi
    def _is_restocking_fee_chargeable(self):
        self.ensure_one()
        if not self.charge_restocking_fee:
            return False
        if not self.origin_returned_move_id:
            return False
        return True
