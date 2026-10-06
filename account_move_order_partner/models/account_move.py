# Copyright 2025 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    order_partner_id = fields.Many2one(
        "res.partner",
        string="Sold-to Partner",
        compute="_compute_order_partner_id",
        store=True,
    )

    @api.depends(
        "move_type", "partner_id", "invoice_line_ids.sale_line_ids.order_partner_id"
    )
    def _compute_order_partner_id(self):
        for move in self:
            move.order_partner_id = move.partner_id
            sale_partners = move.move_type in [
                "out_invoice",
                "out_refund",
            ] and move.invoice_line_ids.mapped("sale_line_ids.order_partner_id")
            if sale_partners and len(sale_partners) == 1:
                move.order_partner_id = sale_partners.id
