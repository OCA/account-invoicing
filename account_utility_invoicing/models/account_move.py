# Copyright 2025 Ecosoft Co., Ltd (https://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    is_utility = fields.Boolean(string="Utility")

    def _post(self, soft=True):
        """Update last reading after invoice posted"""
        posted = super()._post(soft=soft)
        for line in posted._get_utility_lines_update_reading():
            line.utility_line_id.utility_id.write({"last_reading": line.curr_unit})
        return posted

    def _get_utility_lines_update_reading(self):
        return self.line_ids.filtered(
            lambda line: line.move_id.is_utility
            and line.utility_line_id
            and line.utility_line_id.utility_type_id.update_last_reading
        )


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    utility_line_id = fields.Many2one(
        comodel_name="account.utility.line",
        string="Utility",
        index=True,
    )
    prev_unit = fields.Integer()
    curr_unit = fields.Integer()

    @api.onchange("prev_unit", "curr_unit")
    def _onchange_utility_prev_curr(self):
        if self.move_id.is_utility:
            self.quantity = self.curr_unit - self.prev_unit
