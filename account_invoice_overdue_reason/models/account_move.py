# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    overdue_reason_id = fields.Many2one(comodel_name="account.move.overdue.reason")
    show_overdue_reason = fields.Boolean(compute="_compute_show_overdue_reason")

    @api.depends("invoice_date_due", "move_type")
    def _compute_show_overdue_reason(self):
        today = fields.Date.context_today(self)
        for move in self:
            move.show_overdue_reason = (
                move.move_type == "out_invoice"
                and move.invoice_date_due
                and move.invoice_date_due < today
            )
