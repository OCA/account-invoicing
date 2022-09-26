# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    invoicing_mode_monthly_day_todo = fields.Integer(
        "Invoicing Day",
        default="31",
        help="Day of the month to execute the invoicing. For a number higher"
        "than the number of days in a month, the invoicing will be"
        "executed on the last day of the month.",
    )
    invoicing_mode_monthly_last_execution = fields.Datetime(
        string="Last execution",
        help="Last execution of monthly invoicing.",
        readonly=True,
    )
