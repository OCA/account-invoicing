# Copyright 2022 Therp BV <https://therp.nl>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models


class AccountProductMoveLine(models.Model):
    _name = "account.product.move.line"
    _description = "Items for journal entry for given products"

    move_id = fields.Many2one(comodel_name="account.product.move")
    company_id = fields.Many2one(
        related="move_id.company_id", store=True, readonly=True
    )
    company_currency_id = fields.Many2one(
        related="company_id.currency_id",
        string="Company Currency",
        readonly=True,
        help="Utility field to express amount currency",
    )
    debit = fields.Monetary(default=0.0, currency_field="company_currency_id")
    credit = fields.Monetary(default=0.0, currency_field="company_currency_id")
    account_id = fields.Many2one(
        comodel_name="account.account",
        ondelete="cascade",
        required=True,
        check_company=True,
    )
    currency_id = fields.Many2one("res.currency", string="Currency")
    amount_currency = fields.Monetary(
        string="Amount in Currency",
        copy=True,
        help="The amount expressed in an optional other currency"
        " if it is a multi-currency entry.",
    )

    @api.model_create_multi
    def create(self, vals_list):
        """Make sure debit and credit reflect currency fields."""
        result = super().create(vals_list)
        result._recompute_debit_credit_from_amount_currency()
        return result

    def write(self, vals):
        """Make sure debit and credit reflect currency fields."""
        result = super().write(vals)
        self._recompute_debit_credit_from_amount_currency()
        return result

    @api.onchange("currency_id", "amount_currency")
    def _onchange_amount_currency(self):
        """If currency fields change, change debit/credit."""
        self._recompute_debit_credit_from_amount_currency()

    def _recompute_debit_credit_from_amount_currency(self):
        """Recompute the debit/credit based on amount_currency/currency_id and date."""
        for line in self:
            company_currency = line.company_id.currency_id
            if (
                not company_currency
                or not line.currency_id
                or line.currency_id == company_currency
            ):
                # if no specific currency, leave debit and credit as is.
                continue
            balance = line.currency_id._convert(
                line.amount_currency,
                company_currency,
                line.company_id,
                fields.Date.today(),
            )
            if balance > 0:
                debit = balance
                credit = 0.0
            else:
                debit = 0.0
                credit = -balance
            if debit != line.debit or credit != line.credit:
                # Doing a write only on unequal values prevents infinite recursion.
                line.write({"debit": debit, "credit": credit})
