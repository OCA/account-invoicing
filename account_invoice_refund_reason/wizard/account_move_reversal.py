# Copyright (C) 2019 Open Source Integrators
# Copyright (C) 2019 Serpent Consulting Services Pvt. Ltd.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class AccountMoveReversal(models.TransientModel):
    _inherit = "account.move.reversal"

    reason_id = fields.Many2one("account.invoice.refund.reason", string="Refund Reason")

    @api.onchange("reason_id")
    def _onchange_reason_id(self):
        if self.reason_id:
            self.reason = self.reason_id.name

    def reverse_moves(self):
        res = super().reverse_moves()
        credit_note = self.env["account.move"].browse(res["res_id"])
        credit_note.write({"reason_id": self.reason_id})
        return res
