# Copyright 2025 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    invoice_group_by_order_partner = fields.Boolean(
        related="company_id.invoice_group_by_order_partner", readonly=False
    )
