from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    tax_max_diff_global_rounding_method = fields.Float(
        default=0.0, required=True,
        related='company_id.tax_max_diff_global_rounding_method',
        string='Tax calculation max diff amount for rounding method',
        readonly=False,
    )
