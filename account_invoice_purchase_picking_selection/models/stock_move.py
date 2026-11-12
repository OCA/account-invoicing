from odoo import api, fields, models


class StockMove(models.Model):
    _inherit = "stock.move"

    received_invoiced_line_ids = fields.One2many(
        "account.move.line",
        "stock_move_invoiced_id",
        string="Invoiced Lines",
        copy=False,
    )
    qty_received_invoiced = fields.Float(
        compute="_compute_qty_received_invoiced",
        string="Billed Qty",
        digits="Product Unit of Measure",
        store=True,
    )
    qty_received_to_invoice = fields.Float(
        compute="_compute_qty_received_invoiced",
        string="To Invoice Quantity",
        store=True,
        readonly=True,
        digits="Product Unit of Measure",
    )

    @api.depends(
        "received_invoiced_line_ids.move_id.state",
        "received_invoiced_line_ids.quantity",
        "product_uom_qty",
        "state",
    )
    def _compute_qty_received_invoiced(self):
        for line in self:
            qty = 0.0
            for inv_line in line.received_invoiced_line_ids:
                if inv_line.move_id.state == "cancel":
                    continue
                if inv_line.move_id.move_type == "in_invoice":
                    qty += inv_line.product_uom_id._compute_quantity(
                        inv_line.quantity, line.product_uom
                    )
                elif inv_line.move_id.move_type == "in_refund":
                    qty -= inv_line.product_uom_id._compute_quantity(
                        inv_line.quantity, line.product_uom
                    )
            line.qty_received_invoiced = qty
            line.qty_received_to_invoice = (
                line.product_uom_qty - line.qty_received_invoiced
            )

    def _prepare_account_move_line_from_stock(self, account_move, sequence):
        """
        Prepare account.move.line from stock.move and purchase order line.
        :param account_move: account.move
        :param sequence: int
        :return dict of values for account.move.line
        """
        line_vals = self.purchase_line_id._prepare_account_move_line(account_move)
        quantity = self.qty_received_to_invoice
        if self.product_uom != self.purchase_line_id.product_uom:
            quantity = self.product_uom._compute_quantity(
                quantity, self.purchase_line_id.product_uom
            )
        line_vals.update(
            {
                "sequence": sequence,
                "quantity": quantity,
                "stock_move_invoiced_id": self.id,
            }
        )
        return line_vals
