# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_is_zero


class AccountPayment(models.Model):

    _inherit = "account.payment"

    retention_amount_currency = fields.Monetary(
        string="Suggested Retention",
        compute="_compute_retention_amount_currency",
        store=True,
        help="Expected amount to retain on payment currency",
    )
    enforce_payment_retention = fields.Boolean(
        string="Enforce Retention",
        default=True,
        help="Enforce retention amount as suggested, otherwise, "
        "user can ignore the retention.",
    )
    apply_payment_retention = fields.Boolean(string="Apply Retention")

    @api.onchange("apply_payment_retention")
    def onchange_apply_payment_retention(self):
        amount = abs(
            self._compute_payment_amount(
                self.invoice_ids, self.currency_id, self.journal_id, self.payment_date,
            )
        )
        if self.apply_payment_retention:
            retention_amount = self._get_retention_amount_currency(
                self.invoice_ids, self.currency_id, self.journal_id
            )
            self.amount = amount - retention_amount
            self.payment_difference_handling = "reconcile"
            self.writeoff_account_id = self.env.company.retention_account_id
            self.writeoff_label = self.env.company.retention_account_id.name
        else:
            self.amount = amount
            self.writeoff_account_id = False
            self.writeoff_label = ""

    @api.depends("journal_id", "currency_id")
    def _compute_retention_amount_currency(self):
        for rec in self:
            rec.retention_amount_currency = 0.0
            if rec.currency_id and rec.journal_id:
                rec.retention_amount_currency = self._get_retention_amount_currency(
                    rec.invoice_ids, rec.currency_id, rec.journal_id
                )

    @api.model
    def _get_retention_amount_currency(self, invoices, currency_id, journal_id):
        amount = 0.0
        for invoice in invoices:
            amount += invoice.currency_id._convert(
                invoice.retention_residual_currency,
                currency_id,
                journal_id.company_id,
                fields.Date.today(),
            )
        return amount

    @api.onchange("enforce_payment_retention")
    def _onchange_enforce_payment_retention(self):
        if not self.enforce_payment_retention:
            self.apply_payment_retention = False

    @api.model
    def _compute_payment_amount(self, invoices, currency, journal, date):
        res = super()._compute_payment_amount(invoices, currency, journal, date)
        # res -= self._get_retention_amount_currency(invoices, currency, journal)
        return res

    def _validate_payment_retention(self):
        """If this payment enforce_payment_retention, after reconciliation
        is completed, invoice retention residual should be zero"""
        for record in self:
            if record.enforce_payment_retention:
                invoices = record.invoice_ids
                if not invoices:
                    return
                residual = sum(invoices.mapped("retention_residual_currency"))
                if not float_is_zero(residual, precision_digits=2):
                    raise ValidationError(
                        _(
                            "This payment has retention, please make sure you fill"
                            " in valid retaintion amount and retention account"
                        )
                    )

    def post(self):
        for rec in self:
            invoices = rec.invoice_ids
            if len(invoices) > 1 and invoices.filtered("payment_retention"):
                raise UserError(
                    _(
                        "Selected invoice(s) require payment retentions, "
                        "multi invoices payment is not allowed."
                    )
                )
        res = super().post()
        self._validate_payment_retention()
        return res
