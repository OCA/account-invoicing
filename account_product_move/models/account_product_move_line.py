# Copyright 2022-2023 Therp BV <https://therp.nl>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class AccountProductMoveLine(models.Model):
    _name = "account.product.move.line"
    _description = "Items for journal entry for given products"

    def _compute_effective_currency_id(self):
        """Effective currency is specified on line or taken from company."""
        for line in self:
            line.effective_currency_id = line.currency_id or line.company_currency_id

    company_id = fields.Many2one(
        related="move_id.company_id", store=True, readonly=True
    )
    company_currency_id = fields.Many2one(
        related="company_id.currency_id",
        string="Company Currency",
        readonly=True,
        help="Utility field to express amount currency",
    )
    currency_id = fields.Many2one("res.currency", string="Currency")
    amount_currency = fields.Monetary(
        string="Amount in Currency",
        copy=True,
        help="DEPRECATED, but still needed for data migration",
    )
    effective_currency_id = fields.Many2one(
        comodel_name="res.currency",
        compute="_compute_effective_currency_id",
        string="Effective Currency",
        readonly=True,
        help="Utility field to express amount currency",
    )
    move_id = fields.Many2one(comodel_name="account.product.move")
    account_id = fields.Many2one(
        comodel_name="account.account",
        ondelete="cascade",
        required=True,
        check_company=True,
    )
    debit = fields.Monetary(default=0.0, currency_field="effective_currency_id")
    credit = fields.Monetary(default=0.0, currency_field="effective_currency_id")
    percentage_debit = fields.Float(
        string="Debit as % of cost",
        digits=(5, 2),
        copy=True,
        help="Instead of, or in addition to, a fixed amount debit per unit"
        " product a percentage can be taken from the product standard price.",
    )
    percentage_credit = fields.Float(
        string="Credit as % of cost",
        digits=(5, 2),
        copy=True,
        help="Instead of, or in addition to, a fixed amount credit per unit"
        " product a percentage can be taken from the product standard price.",
    )

    @api.constrains("debit", "credit", "percentage_debit", "percentage_credit")
    def _check_debit_credit(self):
        """Do not allow to mix debit and credit."""
        for line in self:
            if (line.debit or line.percentage_debit) and (
                line.credit or line.percentage_credit
            ):
                raise ValidationError(
                    _("You can not mix debit and credit in one line.")
                )

    @api.constrains(
        "currency_id", "percentage_debit", "percentage_credit",
    )
    def _check_no_percentage_currency(self):
        """Do not use percentages of cost price with currency conversion."""
        for line in self:
            if not line.currency_id or (line.currency_id == line.company_currency_id):
                continue
            if line.percentage_debit or line.percentage_credit:
                raise ValidationError(
                    _("You can only use percentages with the company currency.")
                )

    def _complete_line_vals(self, line, vals):
        """Return dict to complete vals for move line to be created."""
        self.ensure_one()
        vals.update({"name": self.move_id.name, "account_id": self.account_id.id})
        quantity = line.quantity
        invoice_type = line.move_id.type
        standard_price = line.product_id.standard_price
        if self.debit or self.percentage_debit:
            credit = 0.0
            debit = quantity * self.debit
            if self.percentage_debit:
                debit += quantity * self.percentage_debit * 0.01 * standard_price
        else:
            debit = 0.0
            credit = quantity * self.credit
            if self.percentage_credit:
                credit += quantity * self.percentage_credit * 0.01 * standard_price
        if invoice_type == "out_refund":
            # Reverse amounts for credit note.
            debit = 0.0 - debit
            credit = 0.0 - credit
        if self.effective_currency_id == self.company_currency_id:
            vals["debit"] = debit
            vals["credit"] = credit
            vals["currency_id"] = False
        else:
            vals["amount_currency"] = debit - credit
            vals["currency_id"] = self.currency_id.id
        return vals
