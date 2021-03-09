# Copyright 2021 ForgeFlow (http://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class AccountMoveLine(models.Model):
    _inherit = ["account.move.line", "base.exception.method"]
    _name = "account.move.line"

    ignore_exception = fields.Boolean(
        related="move_id.ignore_exception", store=True, string="Ignore Exceptions"
    )

    def _get_main_records(self):
        return self.mapped("move_id")

    @api.model
    def _reverse_field(self):
        return "account_move_ids"

    def _detect_exceptions(self, rule):
        records = super()._detect_exceptions(rule)
        return records.mapped("move_id")
