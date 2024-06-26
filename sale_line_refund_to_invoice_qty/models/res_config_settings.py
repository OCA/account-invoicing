from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    reinvoice_credit_note_default = fields.Boolean(
        related="company_id.reinvoice_credit_note_default",
        readonly=False,
    )
