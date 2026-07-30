# Copyright 2026 Tecnativa - Eduardo Ezerouali
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    avg_price_step_days = fields.Integer(
        related="company_id.avg_price_step_days",
        readonly=False,
    )
    avg_price_max_steps = fields.Integer(
        related="company_id.avg_price_max_steps",
        readonly=False,
    )
