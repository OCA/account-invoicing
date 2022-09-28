# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResCompany(models.Model):

    _inherit = "res.company"

    payconiq_qr_profile_id = fields.Char(
        string="Payconiq Profile Id", help="Fill in this with your payment profile Id"
    )
