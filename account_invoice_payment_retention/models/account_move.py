# Copyright 2020 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class AccountMove(models.Model):
    _inherit = "account.move"

    payment_retention = fields.Selection(
        [("percent", "Percent"), ("amount", "Amount")],
        string="Payment Retention",
        readonly=True,
        states={"draft": [("readonly", False)]},
        help="Suggested retention amount to be withheld on payment.\n"
        "Note: as a suggestiong, during payment, user can ignore it.",
    )
    amount_retention = fields.Float(
        string="Retention",
        readonly=True,
        states={"draft": [("readonly", False)]},
        help="Retention in percent of this invoice, or by amount",
    )
    retention_amount_currency = fields.Monetary(
        string="Retention Amount",
        compute="_compute_retention_amount_currency",
        store=True,
        help="Based on retention type, this field show the amount to retain.",
    )
    retention_residual_currency = fields.Monetary(
        string="Retention Residual",
        compute="_compute_retention_residual_currency",
    )
    retained_move_ids = fields.Many2many(
        comodel_name="account.move",
        relation="account_invoice_move_rel",
        column1="invoice_id",
        column2="move_id",
        string="Return Retention",
        readonly=True,
        states={"draft": [("readonly", False)]},
        copy=False,
    )

    @api.onchange("payment_retention")
    def _onchange_payment_retention(self):
        self.amount_retention = False
        self.retained_move_ids = False

    @api.onchange("partner_id")
    def _onchange_domain_retained_move_ids(self):
        self.retained_move_ids = False
        domain = []
        if self.env.user.has_group(
            "account_invoice_payment_retention.group_payment_retention"
        ):
            dom = [
                ("parent_state", "=", "posted"),
                ("account_id", "=", self.env.company.retention_account_id.id),
                ("reconciled", "=", False),
                ("partner_id", "=", self.partner_id.id),
            ]
            move_lines = self.env["account.move.line"].search(dom)
            move_ids = move_lines.mapped("move_id").ids
            domain = [("id", "in", move_ids)]
        return {"domain": {"retained_move_ids": domain}}

    @api.model
    def _move_lines_retained_moves(self, retained_moves):
        """ Get move_lines from selected retained moves in list of dict """
        retained_move_lines = []
        retention_account = self.env.company.retention_account_id
        move_lines = retained_moves.mapped("line_ids").filtered(
            lambda l: l.account_id == retention_account and not l.reconciled
        )
        for line in move_lines:
            copied_vals = line.copy_data()[0]
            debit = copied_vals["debit"]
            credit = copied_vals["credit"]
            copied_vals["debit"] = credit
            copied_vals["credit"] = debit
            copied_vals["amount_currency"] = False
            copied_vals["currency_id"] = False
            copied_vals["move_id"] = self.id
            copied_vals["price_unit"] = credit + debit
            copied_vals["price_subtotal"] = (
                copied_vals["quantity"] * copied_vals["price_unit"]
            )
            retained_move_lines.append(copied_vals)
        return retained_move_lines

    @api.onchange("retained_move_ids")
    def _onchange_retained_move_ids(self):
        self.line_ids = False
        self.payment_retention = False
        if self.retained_move_ids:
            lines = self._move_lines_retained_moves(self.retained_move_ids)
            for line in lines:
                self.env["account.move.line"].new(line)
        self.currency_id = self.env.company.currency_id
        self._recompute_dynamic_lines()

    @api.depends("payment_retention", "amount_retention", "amount_untaxed")
    def _compute_retention_amount_currency(self):
        """ Compute retention based on untaxed amount """
        for rec in self:
            amount = 0.0
            if rec.payment_retention == "amount":
                amount = rec.amount_retention
            elif rec.payment_retention == "percent":
                # Ensure working with purchase deposit, sum only positive qty lines
                amount_untaxed = sum(
                    rec.invoice_line_ids.filtered(lambda l: l.quantity > 0).mapped(
                        "amount_currency"
                    )
                )
                sign = 1 if rec.move_type in ["in_invoice", "out_refund"] else -1
                amount = sign * (amount_untaxed * rec.amount_retention / 100)
            rec.retention_amount_currency = amount

    def _get_retained_move_lines(self, retained_invoice):
        move_lines = retained_invoice.line_ids
        reconciled_moves = move_lines.mapped(
            "matched_debit_ids.debit_move_id.move_id"
        ) + move_lines.mapped("matched_credit_ids.credit_move_id.move_id")
        retention_account = self.env.company.retention_account_id
        retained_move_lines = reconciled_moves.mapped("line_ids").filtered(
            lambda l: l.account_id == retention_account
        )
        return retained_move_lines

    @api.depends("line_ids.matched_debit_ids", "line_ids.matched_credit_ids")
    def _compute_retention_residual_currency(self):
        """ Expected retention amount minus payment retention """
        for rec in self:
            if not rec.payment_retention:
                rec.retention_residual_currency = 0.0
                continue
            retained_moves = self._get_retained_move_lines(rec)
            retained = 0.0
            sign = 1 if rec.move_type in ["in_invoice", "out_refund"] else -1
            if rec.currency_id == rec.company_currency_id:
                retained = sum(retained_moves.mapped("balance"))
            else:
                for move in retained_moves:
                    retained += rec.company_currency_id._convert(
                        move.balance, rec.currency_id, rec.company_id, move.date
                    )
            rec.retention_residual_currency = rec.retention_amount_currency + (
                sign * retained
            )

    @api.constrains("amount_retention", "retention_amount_currency")
    def _check_retention_amount_currency(self):
        for rec in self.filtered("payment_retention"):
            if rec.retention_amount_currency > rec.amount_untaxed:
                raise ValidationError(
                    _("Retention must not exceed the total untaxed amount")
                )

    def action_post(self):
        res = super().action_post()
        for rec in self:
            if self.retained_move_ids:
                retention_account = self.env.company.retention_account_id
                retained_move_lines = self.retained_move_ids.mapped(
                    "line_ids"
                ).filtered(
                    lambda l: l.account_id == retention_account and not l.reconciled
                )
                return_move_lines = rec.line_ids.filtered(
                    lambda l: l.account_id == retention_account
                )
                move_lines = retained_move_lines + return_move_lines
                move_lines.filtered(lambda line: not line.reconciled).reconcile()
        return res
