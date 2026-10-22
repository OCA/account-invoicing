# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    invoicing_mode_fourteen_days_last_execution = fields.Datetime(
        related="company_id.invoicing_mode_fourteen_days_last_execution", readonly=True
    )
