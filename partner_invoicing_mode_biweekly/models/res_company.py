# Copyright 2026 PlanetaTIC - Marc Poch <mpoch@planetatic.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    invoicing_mode_biweekly_day_1 = fields.Integer(
        "First Invoicing Day",
        default=15,
        help="First day of the month to execute the biweekly invoicing.",
    )
    invoicing_mode_biweekly_day_2 = fields.Integer(
        "Second Invoicing Day",
        default=31,
        help="Second day of the month to execute the biweekly invoicing.",
    )
    invoicing_mode_biweekly_last_execution = fields.Datetime(
        string="Last execution (biweekly)",
        help="Last execution of biweekly invoicing.",
    )
