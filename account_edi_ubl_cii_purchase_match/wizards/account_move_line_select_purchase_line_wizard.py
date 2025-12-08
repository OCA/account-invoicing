# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class AccountMoveLineSelectPurchaseLineWizard(models.TransientModel):

    _name = "account.move.line.select.purchase.line.wizard"
    _description = "account move line select purchase line wizard"

    partner_id = fields.Many2one(related="move_line_id.move_id.partner_id")
    description = fields.Char(related="move_line_id.name")
    move_line_id = fields.Many2one(
        comodel_name="account.move.line", readonly=True, required=True
    )
    purchase_order_id = fields.Many2one(
        comodel_name="purchase.order",
        domain="[('partner_id', '=', partner_id), ('state', 'in', ('purchase', 'done'))]",
    )
    purchase_order_line_id = fields.Many2one(
        comodel_name="purchase.order.line",
        string="Line",
        domain="[('order_id', '=', purchase_order_id)]",
    )

    def select_purchase_line(self):
        for rec in self:
            if rec.move_line_id.purchase_line_id:
                continue
            price_unit = rec.move_line_id.price_unit
            rec.move_line_id.product_id = rec.purchase_order_line_id.product_id
            rec.move_line_id.purchase_line_id = rec.purchase_order_line_id
            rec.move_line_id.price_unit = price_unit
            rec.move_line_id._update_product_supplier_name()
