from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    tax_max_diff_global_rounding_method = fields.Float(
        default=0.001,
        digits=(16, 6),
        required=True,
        string="Tax calculation max diff amount for rounding method",
    )
