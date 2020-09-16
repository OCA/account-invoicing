# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class StockReturnPickingLine(models.TransientModel):

    _inherit = "stock.return.picking.line"

    charge_restocking_fee = fields.Boolean(
        help="Tick this box if you wish to charge your customer a fee in "
        "case of return of goods",
        default=False,
    )

    is_customer_return = fields.Boolean(compute="_compute_is_customer_return")

    @api.depends("wizard_id")
    def _compute_is_customer_return(self):
        for rec in self:
            rec.is_customer_return = rec.wizard_id.is_customer_return
