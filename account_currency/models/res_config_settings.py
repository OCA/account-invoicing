# Copyright (C) 2025 Cetmix OÜ
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    company_default_account_currency_id = fields.Many2one(
        related="company_id.default_account_currency_id",
        readonly=False,
    )
