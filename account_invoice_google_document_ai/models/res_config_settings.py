# Copyright 2023 CreuBlanca
# Copyright 2023 ForgeFlow
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):

    _inherit = "res.config.settings"

    ocr_google_project = fields.Char(
        related="company_id.ocr_google_project", readonly=False
    )
    ocr_google_location = fields.Selection(
        related="company_id.ocr_google_location", readonly=False
    )
    ocr_google_processor = fields.Char(
        related="company_id.ocr_google_processor", readonly=False
    )
    ocr_google_enabled = fields.Selection(
        related="company_id.ocr_google_enabled", readonly=False
    )
    ocr_google_authentication = fields.Binary(
        related="company_id.ocr_google_authentication", readonly=False
    )
    ocr_google_authentication_name = fields.Char(
        related="company_id.ocr_google_authentication_name", readonly=False
    )
