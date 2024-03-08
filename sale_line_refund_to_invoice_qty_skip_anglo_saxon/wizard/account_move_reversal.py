# Copyright 2023 ForgeFlow S.L. (https://www.forgeflow.com)
# Part of ForgeFlow. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class AccountMoveReversal(models.TransientModel):

    _inherit = "account.move.reversal"

    editable_sale_qty_to_reinvoice = fields.Boolean()

    @api.onchange("reason_id")
    @api.depends("reason_id.skip_anglo_saxon_entries")
    def _compute_editable_sale_qty_to_reinvoice(self):
        for rec in self:
            rec.editable_sale_qty_to_reinvoice = (
                not rec.reason_id.skip_anglo_saxon_entries
            )

    @api.onchange("reason_id")
    def _onchange_reason(self):
        if self.reason_id:
            self.sale_qty_to_reinvoice = not self.reason_id.skip_anglo_saxon_entries
