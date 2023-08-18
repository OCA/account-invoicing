# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    invoicing_mode_ten_days_last_execution = fields.Datetime(
        string="Last execution (ten days)",
        help="Last execution of ten days invoicing.",
        readonly=True,
    )
