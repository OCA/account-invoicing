# Copyright 2026 Tecnativa - Eduardo Ezerouali
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    avg_price_step_days = fields.Integer(
        string="Average Price Step (days)",
        default=30,
        help="Size in days of each step of the expanding window used to compute "
        "the average purchase (APP) and sale (ASP) prices from invoices.",
    )
    avg_price_max_steps = fields.Integer(
        string="Average Price Max Steps",
        default=12,
        help="Maximum number of steps the window is widened (step size x this "
        "number is the furthest the computation looks back) before giving up.",
    )
