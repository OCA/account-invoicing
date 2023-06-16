# Copyright 2023 Akretion France (http://www.akretion.com/)
# @author: Mourad EL HADJ MIMOUNE <mourad.elhadj.mimounee@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class AccountInvoiceLine(models.Model):
    _inherit = "account.move.line"

    budget_invoice_id = fields.Many2one(
        comodel_name="account.move",
        string="Budget",
        readonly=False,
        index=True,
        domain="["
        "('is_budget', '=', True),"
        "('move_type', '=', 'out_invoice'),"
        "('budget_total_residual', '>', 0.0),"
        "'|', '|', ('partner_id', '=', partner_id), "
        "('partner_id', 'child_of', partner_id), ('partner_id', 'parent_of', partner_id), "
        "],",
    )
    budget_analytic_account_ids = fields.Many2many(
        "account.analytic.account",
        "account_move_budget_analytic_account",
        "invoice_id",
        "analytic_line_id",
        compute="_compute_budget_analytic_account_ids",
        string="Budget Analytic Account",
        copy=False,
        store=True,
    )

    @api.depends("budget_invoice_id")
    def _compute_budget_analytic_account_ids(self):
        for line in self:
            if line.budget_invoice_id:
                move = line.move_id
                budget_analytic_account_ids = line.env["account.analytic.account"]
                for not_budget_line in move.invoice_line_ids.filtered(
                    lambda l: not l.budget_invoice_id
                ):
                    budget_analytic_account_ids |= not_budget_line.mapped(
                        "analytic_line_ids.account_id"
                    )
                line.budget_analytic_account_ids = budget_analytic_account_ids
            else:
                line.budget_analytic_account_ids = line.env["account.analytic.account"]

    @api.constrains("partner_id", "budget_invoice_id")
    def _check_budget_invoice_partner(self):
        for line in self:
            budget_partner = line.budget_invoice_id.partner_id.commercial_partner_id
            if budget_partner and line.partner_id != budget_partner:
                raise UserError(
                    _(
                        "You can not consume a budget of an other customer. "
                        "Please select the right budget"
                    )
                )
