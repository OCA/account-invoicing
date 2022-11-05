# Copyright (C) 2024 Cetmix OÜ
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    invoice_partner_no_autofollow = fields.Boolean(
        config_parameter="invoice_customer_no_autofollow.invoice_partner_no_autofollow",
        string="Customer disable autofollow",
    )
