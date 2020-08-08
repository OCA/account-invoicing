# Copyright 2020 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

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
        readonly=True,
        states={"draft": [("readonly", False)]},
        default=True,
        help="Enforce retention amount as suggested, otherwise, "
        "user can ignore the retention.",
    )
    apply_payment_retention = fields.Boolean(
        string="Apply Retention",
        readonly=True,
        states={"draft": [("readonly", False)]},
    )

    @api.onchange("enforce_payment_retention")
    def _onchange_enforce_payment_retention(self):
        if not self.enforce_payment_retention:
            self.apply_payment_retention = False

    @api.onchange("apply_payment_retention")
    def _onchange_apply_payment_retention(self):
        pay = self._compute_payment_amount(
            self.invoice_ids, self.currency_id, self.journal_id, self.payment_date
        )
        pay = -pay if self.payment_type == "outbound" else pay
        if self.apply_payment_retention:
            self.amount = pay - self.retention_amount_currency
            self.payment_difference_handling = "reconcile"
            self.writeoff_account_id = self.env.company.retention_account_id
            self.writeoff_label = self.env.company.retention_account_id.name
        else:
            self.amount = pay

    @api.depends("journal_id", "currency_id", "invoice_ids", "reconciled_invoice_ids")
    def _compute_retention_amount_currency(self):
        for rec in self:
            rec.retention_amount_currency = 0.0
            if (rec.invoice_ids or rec.reconciled_invoice_ids) and rec.journal_id:
                invoices = rec.reconciled_invoice_ids or rec.invoice_ids
                for invoice in invoices:
                    rec.retention_amount_currency += invoice.currency_id._convert(
                        invoice.retention_residual_currency,
                        rec.currency_id,
                        rec.journal_id.company_id,
                        fields.Date.today(),
                    )

    @api.depends("move_line_ids.matched_debit_ids", "move_line_ids.matched_credit_ids")
    def _compute_reconciled_invoice_ids(self):
        res = super()._compute_reconciled_invoice_ids()
        self._validate_payment_retention()
        return res

    def _validate_payment_retention(self):
        """ If this payment enforce_payment_retention, after reconciliation
            is completed, invoice retention residual should be zero """
        for rec in self.filtered("enforce_payment_retention"):
            invoices = rec.reconciled_invoice_ids
            if not invoices:
                continue
            residual = sum(invoices.mapped("retention_residual_currency"))
            if not float_is_zero(residual, precision_digits=2):
                raise ValidationError(
                    _(
                        "This payment has retention, please make sure you fill"
                        " in valid retaintion amount and retention account"
                    )
                )


class AccountPaymentRegister(models.TransientModel):
    _inherit = "account.payment.register"

    def create_payments(self):
        invoices = self.env["account.move"].browse(self._context.get("active_ids"))
        if invoices.filtered("payment_retention"):
            raise UserError(
                _(
                    "Selected invoice(s) require payment retentions, "
                    "multi invoices payment is not allowed."
                )
            )
        res = super().create_payments()
        return res
