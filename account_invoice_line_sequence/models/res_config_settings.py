# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    invoice_line_sequence_recompute = fields.Boolean(
        related="company_id.invoice_line_sequence_recompute", readonly=False
    )
