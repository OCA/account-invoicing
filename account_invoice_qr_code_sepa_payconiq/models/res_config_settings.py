# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    payconiq_qr_profile_id = fields.Char(
        related="company_id.payconiq_qr_profile_id",
        readonly=False,
    )
    payconiq_url = fields.Char(
        string="Payconiq Base URL",
        config_parameter="account_invoice_qr_code_sepa_payconiq.payconiq_url",
        help="Base URL used to build Payconiq payment links.",
    )
    payconiq_qr_url = fields.Char(
        string="Payconiq QR Portal URL",
        config_parameter="account_invoice_qr_code_sepa_payconiq.payconiq_qr_url",
        help="URL of the Payconiq QR code portal.",
    )
