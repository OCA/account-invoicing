from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    log_ocr_entities_debug = fields.Boolean(
        string="Log OCR Entities as JSON in Chatter",
        related="company_id.log_ocr_entities_debug",
        readonly=False,
    )
