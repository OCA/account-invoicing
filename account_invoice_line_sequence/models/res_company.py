# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    invoice_line_sequence_recompute = fields.Boolean(
        string="Recompute invoice line sequence",
        help="Enable if you want the invoice line sequence to recompute automatically.",
    )
