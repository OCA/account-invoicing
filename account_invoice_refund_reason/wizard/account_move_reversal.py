# Copyright (C) 2019 Open Source Integrators
# Copyright (C) 2019 Serpent Consulting Services Pvt. Ltd.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class AccountMoveReversal(models.TransientModel):
    _inherit = "account.move.reversal"

    reason_id = fields.Many2one("account.move.refund.reason", string="Refund Reason")
    reason = fields.Char(
        compute="_compute_reason", precompute=True, store=True, readonly=False
    )

    @api.depends("reason_id")
    def _compute_reason(self):
        for record in self:
            if record.reason_id:
                record.reason = record.reason_id.name

    def reverse_moves(self):
        res = super().reverse_moves()
        self.move_ids.mapped("reversal_move_id").write({"reason_id": self.reason_id.id})
        return res
