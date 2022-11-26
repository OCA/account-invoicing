from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    so_no_autofollow = fields.Boolean(
        config_parameter="so.no_autofollow", string="Customer disable autofollow"
    )
