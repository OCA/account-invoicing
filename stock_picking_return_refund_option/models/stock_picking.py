# Copyright 2018 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    to_refund_lines = fields.Selection(
        selection=[("to_refund", "To Refund"), ("no_refund", "No Refund")],
        compute="_compute_to_refund_lines",
        inverse="_inverse_to_refund_lines",
        string="Refund Options",
        help="This field allow modify 'to_refund' field value in all "
        "stock moves from this picking after it has been confirmed."
        "to_refund: set all stock moves to True value and recompute "
        "delivered quantities in sale order.\n"
        "no_refund: set all stock moves to False value and recompute "
        "delivered quantities in sale/purchase order.",
    )
    is_return = fields.Boolean(compute="_compute_is_return")

    @api.depends("move_lines.to_refund")
    def _compute_to_refund_lines(self):
        for picking in self:
            moves_to_refund = picking.move_lines.filtered(lambda mv: mv.to_refund)
            if not moves_to_refund:
                picking.to_refund_lines = "no_refund"
            elif len(moves_to_refund) == len(picking.move_lines):
                picking.to_refund_lines = "to_refund"
            else:
                picking.to_refund_lines = False

    def _inverse_to_refund_lines(self):
        """
        Set to_refund stock_move field:
            All lines to True.
            All lines to False.
            Each line to original value selected in return wizard by user.
        """
        for picking in self:
            picking._update_stock_moves()
            picking.set_delivered_qty()
            picking.set_received_qty()

    def _compute_is_return(self):
        for picking in self:
            picking.is_return = any(
                x.origin_returned_move_id for x in picking.move_lines
            )

    def _update_stock_moves(self):
        for pick in self.filtered("to_refund_lines"):
            pick.move_lines.write({"to_refund": pick.to_refund_lines == "to_refund"})

    def set_delivered_qty(self):
        """
        Check if exists sale_line_id field in stock.move model that has been
        added by sale_stock module, this module has not dependency of this,
        Update sale order line qty_delivered for allow do a refund invoice
        """
        if hasattr(self.env["stock.move"], "sale_line_id") and self.sale_id:
            # The sale_stock module is installed
            so_lines = self.mapped("move_lines.sale_line_id").filtered(
                lambda x: x.product_id.invoice_policy in ("order", "delivery")
            )
            so_lines._compute_qty_delivered()

    def set_received_qty(self):
        """
        Check if exists purchase_line_id field in stock.move model that has
        been added by purchase module, this module has not dependency of this,
        Update purchase order line qty_received for allow do a refund invoice.
        """
        if hasattr(self.env["stock.move"], "purchase_line_id") and self.purchase_id:
            # The purchase module is installed
            po_lines = self.mapped("move_lines.purchase_line_id").filtered(
                lambda x: x.product_id.invoice_policy in ("order", "delivery")
            )
            po_lines._compute_qty_received()
