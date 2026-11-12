from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    reinvoice_credit_note_default = fields.Boolean(
        "Reinvoice credit notes by default", default=True
    )
