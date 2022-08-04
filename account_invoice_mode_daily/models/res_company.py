# Copyright 2021 Camptocamp SA
# Copyright 2022 manaTec GmbH
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    daily_invoicing_mode_last_execution = fields.Datetime(
        string="Daily last execution",
        help="Last execution of daily invoice/refunds creation.",
        readonly=True,
    )
