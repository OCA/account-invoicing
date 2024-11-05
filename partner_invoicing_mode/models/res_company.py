# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    invoicing_mode_standard_last_execution = fields.Datetime(
        string="Last execution (standard)",
        help="Last execution of standard invoicing.",
    )
