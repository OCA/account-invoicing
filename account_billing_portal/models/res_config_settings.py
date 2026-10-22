# Copyright 2025 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    billing_email_template_id = fields.Many2one(
        related="company_id.billing_email_template_id",
        readonly=False,
    )
