# Copyright 2022-2023 Therp BV <https://therp.nl>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import _, api, fields, models
from odoo.tools import UserError
from odoo.tools.float_utils import float_is_zero


class AccountProductMove(models.Model):
    _name = "account.product.move"
    _description = "Template for additional journal entries/items"

    @api.depends("journal_id")
    def _compute_company_id(self):
        """Company must correspond to journal."""
        for move in self:
            move.company_id = (
                move.journal_id.company_id or move.company_id or self.env.company
            )

    name = fields.Char(required=True, copy=False, default="New")
    state = fields.Selection(
        selection=[("new", "New"), ("complete", "Complete")],
        default="new",
        required=True,
    )
    product_category_ids = fields.Many2many(
        comodel_name="product.category",
        help="Journal items will be created for these product categories",
    )
    product_tmpl_ids = fields.Many2many(
        comodel_name="product.template",
        help="Journal items will be created for these products",
    )
    journal_id = fields.Many2one(comodel_name="account.journal", required=True)
    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Company",
        store=True,
        readonly=True,
        compute="_compute_company_id",
    )
    line_ids = fields.One2many(
        comodel_name="account.product.move.line",
        inverse_name="move_id",
        copy=True,
        string="Extra Journal Items",
        states={"complete": [("readonly", True)]},
        help="Journal items to be added in new journal entry",
    )
    filter_id = fields.Many2one(
        comodel_name="ir.filters",
        string="Filter to apply on moves",
        domain=[("model_id", "=", "account.move"), ("user_id", "=", False)],
    )
    active = fields.Boolean(default=True)

    def button_complete(self):
        """Setting move to complete."""
        self.ensure_one()
        self._check_balanced()
        self.state = "complete"

    def button_reset(self):
        """Setting move to new."""
        self.ensure_one()
        self.state = "new"

    def action_toggle_active(self):
        self.ensure_one()
        self.active = not self.active

    def _check_balanced(self):
        """Applying all extra move lines should leave total move balanced."""
        self.ensure_one()
        if not self.line_ids:
            return
        lines_per_currency = self._collect_lines_per_currency()
        for currency_name, currency_entry in lines_per_currency.items():
            debit = currency_entry["debit"]
            credit = currency_entry["credit"]
            if not float_is_zero(debit - credit, 3):
                raise UserError(
                    _(
                        "Cannot create unbalanced product move for currency %s.\n"
                        "Debit = %s, credit = %s."
                    )
                    % (currency_name, debit, credit)
                )
            percentage_debit = currency_entry["percentage_debit"]
            percentage_credit = currency_entry["percentage_credit"]
            if not float_is_zero(percentage_debit - percentage_credit, 3):
                raise UserError(
                    _(
                        "Cannot create unbalanced product move for currency %s.\n"
                        "Debit percentage = %s, credit percentage = %s."
                    )
                    % (currency_name, percentage_debit, percentage_credit)
                )

    def _collect_lines_per_currency(self):
        """Per currency collect debit and credit amounts and percentages."""
        self.ensure_one()
        if not self.line_ids:
            return {}
        lines_per_currency = {}
        # Setup manual loop, instead of using sum to prevent repeated
        # iteration over the same records.
        for line in self.line_ids:
            currency_name = line.effective_currency_id.name
            if currency_name not in lines_per_currency:
                lines_per_currency[currency_name] = {
                    "debit": 0.0,
                    "credit": 0.0,
                    "percentage_debit": 0.0,
                    "percentage_credit": 0.0,
                }
            currency_entry = lines_per_currency[currency_name]
            currency_entry["debit"] += line.debit
            currency_entry["credit"] += line.credit
            currency_entry["percentage_debit"] += line.percentage_debit
            currency_entry["percentage_credit"] += line.percentage_credit
        return lines_per_currency
