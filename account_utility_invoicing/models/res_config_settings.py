# Copyright 2025 Ecosoft Co., Ltd (https://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    journal_account_utility_id = fields.Many2one(
        related="company_id.journal_account_utility_id",
        readonly=False,
    )
    utility_rounding_method = fields.Selection(
        related="company_id.utility_rounding_method",
        readonly=False,
    )
