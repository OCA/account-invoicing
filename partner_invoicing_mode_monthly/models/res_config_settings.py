# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    res_invoicing_mode_monthly_day_todo = fields.Integer(
        related="company_id.invoicing_mode_monthly_day_todo", readonly=False
    )
    invoicing_mode_monthly_last_execution = fields.Datetime(
        related="company_id.invoicing_mode_monthly_last_execution", readonly=True
    )
