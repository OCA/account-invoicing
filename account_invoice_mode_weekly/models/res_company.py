# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    invoicing_mode_weekly_day_todo = fields.Selection(
        selection=[
            ("0", "Monday"),
            ("1", "Tuesday"),
            ("2", "Wednesday"),
            ("3", "Thursday"),
            ("4", "Friday"),
            ("5", "Saturday"),
            ("6", "Sunday"),
        ],
        default="0",
        string="Weekly Invoicing Day",
        help="Day of the week to execute the invoicing.",
    )
    invoicing_mode_weekly_last_execution = fields.Datetime(
        string="Weekly last execution",
        help="Last execution of weekly invoicing.",
        readonly=True,
    )
