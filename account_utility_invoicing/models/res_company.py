# Copyright 2025 Ecosoft Co., Ltd. (<http://ecosoft.co.th>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    journal_account_utility_id = fields.Many2one(
        comodel_name="account.journal",
    )
    utility_rounding_method = fields.Selection(
        selection=[
            ("round_per_line", "Round per Line"),
            ("round_globally", "Round Globally"),
        ],
        default="round_per_line",
    )
