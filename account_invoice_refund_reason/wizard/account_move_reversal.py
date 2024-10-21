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
        """Define: Compute Reversal Reason

        Compute the reason based on the selected reason ID.

        :return: None
        """
        for record in self:
            record.reason = record.reason_id and record.reason_id.name or ""

    def reverse_moves(self, is_modify=False):
        """Override: Reverse Moves

        To set the reason_id fields in the new created refunds.

        :param is_modify: Boolean
        :return: Super call returned value
        """

        res = super().reverse_moves(is_modify=is_modify)
        self.move_ids.mapped("reversal_move_id").filtered(
            lambda x: not x.reason_id
        ).write({"reason_id": self.reason_id.id})
        return res
