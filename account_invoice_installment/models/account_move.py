# Copyright 2021 Eder Brito
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class AccountMove(models.Model):

    _inherit = "account.move"

    receivable_move_line_ids = fields.Many2many(
        comodel_name="account.move.line",
        string="Receivables",
        compute="_compute_receivable_move_line_ids",
    )

    payable_move_line_ids = fields.Many2many(
        comodel_name="account.move.line",
        string="Payables",
        compute="_compute_payable_move_line_ids",
    )

    @api.depends("line_ids")
    def _compute_receivable_move_line_ids(self):
        for move in self:
            move.receivable_move_line_ids = move.line_ids.filtered(
                lambda m: m.account_id.user_type_id.type == "receivable"
            ).sorted(key=lambda m: m.date_maturity)

    @api.depends("line_ids")
    def _compute_payable_move_line_ids(self):
        for move in self:
            move.payable_move_line_ids = move.line_ids.filtered(
                lambda m: m.account_id.user_type_id.type == "payable"
            ).sorted(key=lambda m: m.date_maturity)
