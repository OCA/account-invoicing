# Copyright 2023 CreuBlanca
# Copyright 2023 ForgeFlow
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    ocr_google_project = fields.Char()
    ocr_google_location = fields.Selection([("eu", "Europe"), ("us", "United States")])
    ocr_google_processor = fields.Char()
    ocr_google_authentication = fields.Binary()
    ocr_google_authentication_name = fields.Binary()
    ocr_google_enabled = fields.Boolean()
