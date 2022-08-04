# Copyright 2022 manaTec GmbH
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    invoicing_mode_daily_last_execution = fields.Datetime(
        related="company_id.daily_invoicing_mode_last_execution",
        readonly=True,
    )
