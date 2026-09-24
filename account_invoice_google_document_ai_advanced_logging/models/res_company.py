from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    log_ocr_entities_debug = fields.Boolean(
        string="Log OCR Entities as JSON in Chatter",
        copy=False,
    )
