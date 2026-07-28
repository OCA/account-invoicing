from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    google_ocr_invoice_mode = fields.Selection(
        selection_add=[("single_line_total", "Single Line Total Mode")],
    )
