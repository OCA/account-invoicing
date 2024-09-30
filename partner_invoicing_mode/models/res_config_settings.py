# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    invoicing_mode_standard_last_execution = fields.Datetime(
        related="company_id.invoicing_mode_standard_last_execution"
    )
