# Copyright 2020 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_is_zero


class AccountPaymentRegister(models.TransientModel):
    _inherit = "account.payment.register"

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

    @api.depends("journal_id", "currency_id")
    def _compute_retention_amount_currency(self):
        for rec in self:
            rec.retention_amount_currency = 0.0
            invoices = rec.line_ids.move_id
            for invoice in invoices:
                rec.retention_amount_currency += invoice.currency_id._convert(
                    invoice.retention_residual_currency,
                    rec.currency_id,
                    rec.journal_id.company_id,
                    fields.Date.today(),
                )

    @api.onchange("enforce_payment_retention")
    def _onchange_enforce_payment_retention(self):
        if not self.enforce_payment_retention:
            self.apply_payment_retention = False

    @api.depends(
        "source_amount",
        "source_amount_currency",
        "source_currency_id",
        "company_id",
        "currency_id",
        "payment_date",
        "apply_payment_retention",
    )
    def _compute_amount(self):
        res = super()._compute_amount()
        for rec in self:
            if rec.apply_payment_retention:
                rec.amount -= rec.retention_amount_currency
                rec.payment_difference_handling = "reconcile"
                account = rec.env.company.retention_account_id
                if rec.payment_type == "inbound":
                    account = rec.env.company.retention_receivable_account_id
                rec.writeoff_account_id = account
                rec.writeoff_label = account.name
        return res

    def _validate_payment_retention(self):
        """If this payment enforce_payment_retention, after reconciliation
        is completed, invoice retention residual should be zero"""
        self.ensure_one()
        if self.enforce_payment_retention:
            invoices = self.line_ids.move_id
            residual = sum(invoices.mapped("retention_residual_currency"))
            if not float_is_zero(residual, precision_digits=2):
                raise ValidationError(
                    _(
                        "This payment has retention, please make sure you fill"
                        " in valid retaintion amount and retention account"
                    )
                )

    def action_create_payments(self):
        invoices = self.env["account.move"].browse(self._context.get("active_ids"))
        if len(invoices) > 1 and invoices.filtered("payment_retention"):
            raise UserError(
                _(
                    "Selected invoice(s) require payment retentions, "
                    "multi invoices payment is not allowed."
                )
            )
        res = super().action_create_payments()
        self._validate_payment_retention()
        return res
