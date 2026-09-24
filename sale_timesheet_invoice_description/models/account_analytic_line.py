# Copyright 2020 Akretion - Clément Mombereau
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class AccountAnalyticLine(models.Model):
    _inherit = "account.analytic.line"

    timesheet_invoice_line_id = fields.Many2one(
        "account.move.line",
        string="Invoice Line",
        readonly=True,
        copy=False,
        help="Invoice line created from the timesheet",
    )
