# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class StockAccountMoveResetToDraft(models.TransientModel):

    _name = "stock.account.move.reset.to.draft"
    _description = "Reset account move to draft"

    move_ids = fields.Many2many(
        comodel_name="account.move",
        compute="_compute_move_ids",
    )
    intertwined_move_line_ids = fields.Many2many(
        comodel_name="account.move.line",
        column1="wizard_id",
        column2="intertwined_move_id",
        relation="stock_account_move_reset_to_draft_intertwined_move_line_rel",
        ondelete="cascade",
        required=True,
        readonly=True,
    )
    consumed_move_line_ids = fields.Many2many(
        comodel_name="account.move.line",
        column1="wizard_id",
        column2="consumed_line_id",
        relation="stock_account_move_reset_to_draft_consumed_move_line_rel",
        ondelete="cascade",
        required=True,
        readonly=True,
    )

    @api.depends("intertwined_move_line_ids", "consumed_move_line_ids")
    def _compute_move_ids(self):
        for wizard in self:
            wizard.move_ids = (
                wizard.consumed_move_line_ids.move_id
                | wizard.intertwined_move_line_ids.move_id
            )

    def doit(self):
        for wizard in self:
            return wizard.move_ids._force_reset_to_draft()
