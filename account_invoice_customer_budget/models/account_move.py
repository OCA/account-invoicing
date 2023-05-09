# Copyright 2023 Akretion France (http://www.akretion.com/)
# @author: Mourad EL HADJ MIMOUNE <mourad.elhadj.mimounee@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class AccountMove(models.Model):
    _inherit = "account.move"

    budget_invoice_consumption_ids = fields.Many2many(
        "account.move",
        "account_move_budget_invoice",
        "invoice_id",
        "inv_budget_id",
        compute="_compute_budget_consumption_invoice",
        string="Budget consumption invoices",
        copy=False,
        store=True,
    )
    budget_consumption_invoice_count = fields.Integer(
        compute="_compute_budget_consumption_invoice",
        string="Budget invoices consumption Count",
        copy=False,
        default=0,
        store=True,
    )
    budget_consumption_line_ids = fields.One2many(
        "account.move.line",
        "budget_invoice_id",
        string="Budget Consumption Lines",
        readonly=True,
        copy=False,
    )
    budget_total_consumption = fields.Monetary(
        string="Budget consumption",
        compute="_compute_budget_total_consumptions",
        store=False,
        currency_field="currency_id",
    )
    budget_total_residual = fields.Monetary(
        string="Budget residual total",
        compute="_compute_budget_total_consumptions",
        store=False,
        currency_field="currency_id",
    )
    budget_untaxed_consumption = fields.Monetary(
        string="Budget untaxed consumption",
        compute="_compute_budget_total_consumptions",
        store=False,
        currency_field="currency_id",
    )
    budget_untaxed_residual = fields.Monetary(
        string="Budget untaxed residual",
        compute="_compute_budget_total_consumptions",
        store=False,
        currency_field="currency_id",
    )
    is_budget = fields.Boolean("Is a budget", related="journal_id.is_budget")
    budget_account_ids = fields.Many2many(
        "account.account",
        "account_move_budget_account",
        "account_id",
        "inv_id",
        compute="_compute_budget_account",
        string="budget account",
        copy=False,
        store=True,
        help="Technical field used to validate line budget consumption account",
    )
    analytic_line_count = fields.Integer(
        string="Analytic Lines Count", compute="_compute_used_analytic_line_ids"
    )
    analytic_line_ids = fields.Many2many(
        comodel_name="account.analytic.line",
        string="Analytic Lines",
        compute="_compute_used_analytic_line_ids",
        copy=False,
    )

    @api.depends(
        "budget_consumption_line_ids.price_total",
        "budget_consumption_line_ids.parent_state",
    )
    def _compute_budget_total_consumptions(self):
        for move in self:
            budget_total_consumption = 0.0
            budget_untaxed_consumption = 0.0
            for line in move.budget_consumption_line_ids.filtered(
                lambda l: l.parent_state != "cancel"
            ):
                if move.is_invoice(True):
                    # === Invoices ===
                    # budget_total_consumption amount.
                    budget_total_consumption += line.price_total
                    budget_untaxed_consumption += line.price_subtotal
                else:
                    # === Miscellaneous journal entry ===
                    if line.debit:
                        budget_total_consumption += line.balance
                        budget_untaxed_consumption += line.balance
            move.budget_total_consumption = budget_total_consumption
            move.budget_untaxed_consumption = budget_untaxed_consumption
            move.budget_total_residual = move.amount_total - (-budget_total_consumption)
            move.budget_untaxed_residual = move.amount_untaxed - (
                -budget_untaxed_consumption
            )

    @api.depends(
        "journal_id",
        "journal_id.is_budget",
    )
    def _compute_budget_account(self):
        for move in self:
            move.budget_account_ids = False
            if not move.is_budget:
                continue
            invoice_lines = move.invoice_line_ids.filtered(
                lambda l: "product" == l.display_type
            )
            accounts = invoice_lines.mapped("account_id")
            move.budget_account_ids = accounts

    @api.depends("invoice_line_ids.budget_invoice_id")
    def _compute_budget_consumption_invoice(self):
        for move in self:
            invoices = move.mapped("invoice_line_ids.budget_invoice_id")
            move.budget_invoice_consumption_ids = invoices
            move.budget_consumption_invoice_count = len(invoices)

    @api.depends("invoice_line_ids.analytic_line_ids")
    def _compute_used_analytic_line_ids(self):
        # The analytic_line_ids are obtained thanks to the invoice lines
        for move in self:
            analytic_line_ids = move.mapped("invoice_line_ids.analytic_line_ids")
            move.analytic_line_ids = analytic_line_ids
            move.analytic_line_count = len(analytic_line_ids)

    def action_post(self):
        for inv in self:
            if inv.is_budget and not inv.journal_id.account_control_ids:
                raise ValidationError(
                    _(
                        "Please check your the budget journla advenced setting!\n"
                        "You may define allowed accounts for budget account journal: "
                        "(%(budget_name)s)!\n"
                        "Allowed account must contain prepaid revenue account with a "
                        "receivable account and vat account.\n"
                    )
                    % {
                        "budget_name": inv.journal_id.name,
                    }
                )

            if inv.move_type != "out_invoice" and inv.budget_invoice_consumption_ids:
                raise ValidationError(
                    _(
                        "Please verify the budget consumption of the invoice!\n"
                        "You can use budget consumption only for Customer invoice\n"
                        "Used budgets are (%(budget_numbers)s)!\n"
                    )
                    % {
                        "budget_numbers": ",".join(
                            [str(bg.name) for bg in inv.budget_invoice_consumption_ids]
                        ),
                    }
                )

            invoice_lines = inv.invoice_line_ids.filtered(
                lambda l: "product" == l.display_type
            )

            budget_amounts = {}
            # Test budget account and budget amount availability
            for line in invoice_lines:
                if line.budget_invoice_id:
                    budget_amounts.setdefault(
                        line.budget_invoice_id, {"price_total": 0.0}
                    )
                    budget_amounts[line.budget_invoice_id][
                        "price_total"
                    ] += line.price_total
                    authorized_accounts = line.budget_invoice_id.budget_account_ids
                    if line.account_id not in authorized_accounts:
                        raise ValidationError(
                            _(
                                "Please verify the account of budget consumption line!\n"
                                "You can use only the following accounts in budget "
                                "consumption line.\n"
                                "Authorized accounts (%(authorized_accounts)s)!\n"
                            )
                            % {
                                "authorized_accounts": ",".join(
                                    [str(abg.code) for abg in authorized_accounts]
                                ),
                            }
                        )
            for budget, _price_total in budget_amounts.items():
                if budget.budget_total_residual < 0:
                    consumption_amount = round(_price_total["price_total"], 2)
                    avalaible_amount = round(
                        abs(budget.budget_total_residual - _price_total["price_total"]),
                        2,
                    )
                    raise ValidationError(
                        _(
                            "Please check the amount avalaible of budget %(budget_name)s:\n"
                            "Consumption amount: %(consumption_amount)s !\n"
                            "Avalaible amount: %(avalaible_amount)s !\n"
                            "This amount are taxed !\n"
                        )
                        % {
                            "budget_name": f"{budget.name}",
                            "consumption_amount": f"{consumption_amount}",
                            "avalaible_amount": f"{avalaible_amount}",
                        }
                    )

        return super().action_post()
