# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class StockReturnPicking(models.TransientModel):

    _inherit = "stock.return.picking"

    charge_customer_stock_return = fields.Boolean(
        string="Charge fees",
        help="Tick this box if you wish to charge your customer a fee in "
        "case of return of goods. Default value comes from the customer "
        "info.",
        default=False,
    )
    is_customer_return = fields.Boolean(readonly=True)

    @api.model
    def default_get(self, fields):  # pylint: disable=redefined-outer-name
        res = super(StockReturnPicking, self).default_get(fields)
        if not (
            "charge_customer_stock_return" in fields
            or "product_return_moves" in fields
            or "is_customer_return" in fields
        ):
            return res
        picking = self.env["stock.picking"].browse(
            self.env.context["active_id"]
        )
        charge_customer_stock_return = (
            picking.partner_id.charge_customer_stock_return
        )
        if "is_customer_return" in fields:
            res["is_customer_return"] = (
                picking.location_dest_id.usage == "customer"
            )
        if "charge_customer_stock_return" in fields:
            res["charge_customer_stock_return"] = charge_customer_stock_return
        if "product_return_moves" in fields:
            for move in res.get("product_return_moves", []):
                # item are tuple to create move (0, 0, {..})
                move[2][
                    "charge_customer_stock_return"
                ] = charge_customer_stock_return
        return res

    @api.onchange("charge_customer_stock_return")
    def _onchange_charge_customer_stock_return(self):
        for move in self.product_return_moves:
            move.charge_customer_stock_return = (
                self.charge_customer_stock_return
            )

    @api.multi
    def _create_returns(self):
        new_picking_id, new_picking_type_id = super(
            StockReturnPicking, self
        )._create_returns()
        self.ensure_one()
        if self.is_customer_return:
            new_picking = self.env["stock.picking"].browse(new_picking_id)
            # we must update the stock moves after the creation since there is
            # no hooks where to enrich the data used to create the moves :-(
            new_move_by_returned_move = {
                l.origin_returned_move_id: l for l in new_picking.move_lines
            }
            return_line_by_returned_move = {
                l.move_id: l for l in self.product_return_moves
            }
            for returned_move, new_move in new_move_by_returned_move.items():
                new_move.charge_customer_stock_return = \
                    return_line_by_returned_move[
                        returned_move
                    ].charge_customer_stock_return
        return new_picking_id, new_picking_type_id
