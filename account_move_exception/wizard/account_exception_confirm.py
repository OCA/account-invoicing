# Copyright 2021 ForgeFlow (http://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class AccountExceptionConfirm(models.TransientModel):
    _name = "account.exception.confirm"
    _description = "Account exception wizard"
    _inherit = ["exception.rule.confirm"]

    related_model_id = fields.Many2one(
        comodel_name="account.move", string="Journal Entry"
    )

    def action_confirm(self):
        self.ensure_one()
        if self.ignore:
            self.related_model_id.button_draft()
            self.related_model_id.ignore_exception = True
            self.related_model_id.action_post()
        return super().action_confirm()
