# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    payconiq_qr_profile_id = fields.Char(
        related="company_id.payconiq_qr_profile_id",
        readonly=False,
    )
