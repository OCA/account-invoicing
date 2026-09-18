# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    original_partner_ids = fields.Many2many(
        comodel_name="res.partner",
        relation="account_move_original_partner_rel",
        column1="account_move_id",
        column2="res_partner_id",
        compute="_compute_original_partner_ids",
        store=True,
        string="Original Partners",
    )

    @api.depends("move_type", "invoice_line_ids.sale_line_ids.order_id.partner_id")
    def _compute_original_partner_ids(self):
        for move in self:
            move.original_partner_ids = (
                move.move_type == "out_invoice"
                and move.invoice_line_ids.mapped("sale_line_ids.order_id.partner_id")
            )
