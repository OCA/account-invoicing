# Copyright 2026 PlanetaTIC - Marc Poch <mpoch@planetatic.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    res_invoicing_mode_biweekly_day_1 = fields.Integer(
        related="company_id.invoicing_mode_biweekly_day_1", readonly=False
    )
    res_invoicing_mode_biweekly_day_2 = fields.Integer(
        related="company_id.invoicing_mode_biweekly_day_2", readonly=False
    )
    res_invoicing_mode_biweekly_last_execution = fields.Datetime(
        related="company_id.invoicing_mode_biweekly_last_execution"
    )
