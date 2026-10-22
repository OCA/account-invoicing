# Copyright 2021 ForgeFlow (http://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class AccountMove(models.Model):
    _inherit = ["account.move", "base.exception"]
    _name = "account.move"
    _order = "main_exception_id asc, date desc, name desc"

    @api.model
    def test_all_draft_moves(self):
        move_set = self.search([("state", "=", "draft")])
        move_set.detect_exceptions()
        return True

    @api.model
    def _reverse_field(self):
        return "account_move_ids"

    def detect_exceptions(self):
        all_exceptions = super().detect_exceptions()
        lines = self.mapped("line_ids")
        all_exceptions += lines.detect_exceptions()
        return all_exceptions

    @api.constrains("ignore_exception", "line_ids", "state")
    def account_move_check_exception(self):
        moves = self.filtered(lambda s: s.state == "posted")
        if moves:
            moves._check_exception()

    @api.onchange("line_ids")
    def onchange_ignore_exception(self):
        if self.state == "posted":
            self.ignore_exception = False

    def action_post(self):
        if self.detect_exceptions() and not self.ignore_exception:
            return self._popup_exceptions()
        return super().action_post()

    def button_draft(self):
        res = super().button_draft()
        for order in self:
            order.exception_ids = False
            order.main_exception_id = False
            order.ignore_exception = False
        return res

    @api.model
    def _get_popup_action(self):
        action = self.env.ref("account_move_exception.action_account_exception_confirm")
        return action
