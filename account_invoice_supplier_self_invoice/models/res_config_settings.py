from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    self_invoice_prefix = fields.Char(
        string="Default Self Billing prefix",
        related="company_id.self_invoice_prefix",
        readonly=False,
    )
