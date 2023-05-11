# Copyright 2023 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    @api.depends("invoice_line_ids.analytic_account_id")
    def _compute_analytic_accounts(self):
        for invoice in self:
            invoice.analytic_account_ids = invoice.mapped(
                "invoice_line_ids.analytic_account_id.id"
            )

    def _search_analytic_accounts(self, operator, value):
        return [("invoice_line_ids.analytic_account_id", operator, value)]

    analytic_account_ids = fields.Many2many(
        comodel_name="account.analytic.account",
        compute="_compute_analytic_accounts",
        search="_search_analytic_accounts",
        string="Analytic Account",
        readonly=True,
    )
