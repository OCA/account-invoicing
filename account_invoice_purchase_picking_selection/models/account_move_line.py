from odoo import fields, models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    stock_move_invoiced_id = fields.Many2one(
        "stock.move", string="Stock Move", copy=False, readonly=True
    )
    picking_invoiced_id = fields.Many2one(
        "stock.picking", string="Picking", copy=False, readonly=True
    )
