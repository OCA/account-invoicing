# Copyright 2020 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
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

    @api.depends("journal_id", "currency_id")
    def _compute_retention_amount_currency(self):
        for rec in self:
            rec.retention_amount_currency = 0.0
            moves = rec.line_ids.move_id
            for move in moves:
                rec.retention_amount_currency += move.currency_id._convert(
                    move.retention_residual_currency,
                    rec.currency_id,
                    rec.journal_id.company_id,
                    fields.Date.today(),
                )

    @api.depends(
        "source_amount",
        "source_amount_currency",
        "source_currency_id",
        "company_id",
        "currency_id",
        "payment_date",
        "enforce_payment_retention",
    )
    def _compute_amount(self):
        res = super()._compute_amount()
        for rec in self:
            if rec.enforce_payment_retention:
                rec.amount -= rec.retention_amount_currency
                account = rec.company_id.retention_account_id
                if rec.payment_type == "inbound":
                    account = rec.company_id.retention_receivable_account_id
                rec.write(
                    {
                        "payment_difference_handling": "reconcile",
                        "writeoff_account_id": account.id,
                        "writeoff_label": account.name,
                    }
                )
            else:
                rec.amount += rec.retention_amount_currency
        return res

    def _validate_payment_retention(self):
        """If this payment enforce_payment_retention, after reconciliation
        is completed, move retention residual should be zero"""
        self.ensure_one()
        moves = self.line_ids.move_id
        residual = sum(moves.mapped("retention_residual_currency"))
        if not float_is_zero(residual, precision_digits=2):
            raise ValidationError(
                self.env._(
                    "This payment has retention, please make sure you fill"
                    " in valid retaintion amount and retention account"
                )
            )

    def _create_payments(self):
        moves = self.line_ids.mapped("move_id")
        if len(moves) > 1 and moves.filtered("payment_retention"):
            raise UserError(
                self.env._(
                    "Selected move(s) require payment retentions, "
                    "multi moves payment is not allowed."
                )
            )
        res = super()._create_payments()
        self._validate_payment_retention()
        return res
