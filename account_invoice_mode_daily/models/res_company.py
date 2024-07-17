# Copyright 2023 Michael Tietz (MT Software) <mtietz@mt-software.de>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    invoicing_mode_daily_last_execution = fields.Datetime(
        string="Daily last execution",
        help="Last execution of daily invoice/refunds creation.",
        readonly=True,
    )
