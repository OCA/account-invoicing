# Copyright (C) 2022 ForgeFlow Ltd.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import models


class AccountMove(models.Model):
    _inherit = "account.move"

    def action_post(self):
        res = super(AccountMove, self).action_post()
        for rec in self:
            if rec.move_type == "out_refund" and rec.reason_id.unlink_so:
                rec.invoice_line_ids.sale_line_ids = [
                    (3, line) for line in rec.line_ids.mapped("sale_line_ids.id")
                ]
        return res
