# Copyright 2022 Aures TIC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    invoicing_mode_multi_monthday_last_execution = fields.Datetime(
        related="company_id.invoicing_mode_multi_monthday_last_execution",
        readonly=True,
    )
    invoicing_mode_multi_monthday_days = fields.Char(
        related="company_id.invoicing_mode_multi_monthday_days",
        readonly=False,
    )
