# Copyright (C) 2019 Open Source Integrators
# Copyright (C) 2019 Serpent Consulting Services Pvt. Ltd.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    reason_id = fields.Many2one(
        "account.move.refund.reason", string="Refund Reason", tracking=True
    )
    refund_reason_editable = fields.Boolean(compute="_compute_refund_reason_editable")

    @api.depends("state")
    @api.depends_context("uid")
    def _compute_refund_reason_editable(self):
        # Accounting managers can still correct the reason once posted.
        is_manager = self.env.user.has_group("account.group_account_manager")
        for move in self:
            move.refund_reason_editable = move.state == "draft" or is_manager
