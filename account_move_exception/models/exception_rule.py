# Copyright 2021 ForgeFlow (http://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ExceptionRule(models.Model):
    _inherit = "exception.rule"

    account_move_ids = fields.Many2many(
        comodel_name="account.move", string="Journal Entries"
    )
    model = fields.Selection(
        selection_add=[
            ("account.move", "Account move"),
            ("account.move.line", "Account move line"),
        ],
        ondelete={
            "account.move": "cascade",
            "account.move.line": "cascade",
        },
    )
