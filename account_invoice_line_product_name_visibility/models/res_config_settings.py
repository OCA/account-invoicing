from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    hide_product_name = fields.Boolean(
        string="Hide Product Name",
        related="company_id.hide_product_name",
        readonly=False,
    )
