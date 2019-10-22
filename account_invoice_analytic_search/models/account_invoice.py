# Copyright 2014-2017 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class AccountInvoice(models.Model):

    _inherit = "account.invoice"

    @api.multi
    @api.depends("invoice_line_ids.account_analytic_id")
    def _compute_analytic_accounts(self):
        for invoice in self:
            invoice.account_analytic_ids = invoice.mapped(
                "invoice_line_ids.account_analytic_id.id"
            )

    @api.multi
    def _search_analytic_accounts(self, operator, value):
        return [("invoice_line_ids.account_analytic_id", operator, value)]

    account_analytic_ids = fields.Many2many(
        comodel_name="account.analytic.account",
        compute="_compute_analytic_accounts",
        search="_search_analytic_accounts",
        string="Analytic Account",
        readonly=True,
    )
