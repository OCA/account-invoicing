# Copyright 2025, Kaynnan Lemes <kaynnan.lemes@escodoo.com.br>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class AccountInvoiceAdvanceCompensationWizard(models.TransientModel):
    _name = "account.invoice.advance.compensation.wizard"
    _description = "Invoice Advance Compensation Wizard"

    move_id = fields.Many2one(
        comodel_name="account.move",
        string="Invoice",
        required=True,
        readonly=True,
        default=lambda self: self.env.context.get("default_move_id"),
        help="Invoice to be compensated with an advance.",
    )
    advance_line_id = fields.Many2one(
        comodel_name="account.move.line",
        string="Advance Line",
        domain="[('id', 'in', available_advance_line_ids)]",
        required=True,
        help="The advance line to be used for compensation",
    )
    invoice_line_id = fields.Many2one(
        comodel_name="account.move.line",
        string="Invoice Line",
        domain="[('move_id', '=', move_id), ('amount_residual', '!=', 0)]",
        required=True,
        help="The invoice line to be compensated",
    )
    amount = fields.Monetary(
        string="Compensation Amount",
        currency_field="currency_id",
        required=True,
        help="The amount to be compensated",
    )
    journal_id = fields.Many2one(
        comodel_name="account.journal",
        string="Journal",
        domain="[('is_advance_journal', '=', True)]",
        required=True,
        help="The journal to be used for the compensation entry",
    )
    date = fields.Date(
        string="Compensation Date",
        default=fields.Date.context_today,
        required=True,
        help="The date of the compensation",
    )
    available_advance_line_ids = fields.Many2many(
        comodel_name="account.move.line",
        compute="_compute_available_advance_lines",
        help="Available advance lines for compensation",
    )
    advance_balance = fields.Monetary(
        string="Available Balance",
        compute="_compute_advance_balance",
        currency_field="currency_id",
        readonly=True,
        help="The available balance in the selected advance line",
    )
    currency_id = fields.Many2one(
        comodel_name="res.currency",
        string="Currency",
        compute="_compute_currency",
        store=True,
        readonly=False,
        help="The currency of the compensation",
    )

    @api.depends("journal_id")
    def _compute_currency(self):
        for wizard in self:
            wizard.currency_id = (
                wizard.journal_id.currency_id
                or wizard.journal_id.company_id.currency_id
            )

    @api.depends("move_id", "move_id.partner_id", "move_id.move_type")
    def _compute_available_advance_lines(self):
        for wizard in self:
            wizard.available_advance_line_ids = wizard._get_available_advance_lines()

    @api.depends("advance_line_id")
    def _compute_advance_balance(self):
        for wizard in self:
            wizard.advance_balance = (
                abs(wizard.advance_line_id.amount_residual)
                if wizard.advance_line_id
                else 0
            )

    @api.onchange("invoice_line_id", "advance_line_id")
    def _onchange_invoice_line_id(self):
        if self.invoice_line_id and self.advance_line_id:
            self.amount = min(
                abs(self.invoice_line_id.amount_residual),
                abs(self.advance_line_id.amount_residual),
            )

    def action_confirm_compensation(self):
        self.ensure_one()
        self._validate_compensation()

        move = self._create_compensation_move()
        move.action_post()
        self._process_reconciliation(move)

        return {
            "type": "ir.actions.act_window",
            "res_model": "account.move",
            "res_id": move.id,
            "view_mode": "form",
            "target": "current",
        }

    def _get_available_advance_lines(self):
        move = self.move_id
        if not move or not move.partner_id:
            return self.env["account.move.line"]

        base_domain = [
            ("company_id", "=", move.company_id.id),
            ("move_id.state", "=", "posted"),
            ("move_id.payment_state", "=", "paid"),
            ("partner_id", "=", move.partner_id.id),
            ("account_id.account_type", "=", "asset_prepayments"),
            ("account_id.reconcile", "=", True),
            ("amount_residual", "!=", 0),
        ]

        sign_domain = (
            [("amount_residual", ">", 0)]
            if move.move_type == "in_invoice"
            else [("amount_residual", "<", 0)]
        )
        return self.env["account.move.line"].search(base_domain + sign_domain)

    def _validate_compensation(self):
        if self.amount <= 0:
            raise ValidationError(_("Compensation amount must be greater than zero."))

        if not self.move_id:
            raise ValidationError(_("Invoice is required to create compensation."))

        if self.move_id.state != "posted":
            raise ValidationError(
                _("Only posted invoices and bills can be compensated.")
            )

        if not self.move_id.is_invoice(include_receipts=False):
            raise ValidationError(
                _(
                    "Compensation is available only for customer invoices "
                    "and vendor bills."
                )
            )

        if not self.invoice_line_id:
            raise ValidationError(
                _("Select the invoice line that will be compensated.")
            )

        if self.invoice_line_id.move_id != self.move_id:
            raise ValidationError(
                _("The selected invoice line does not belong to invoice '%s'.")
                % self.move_id.display_name
            )

        if not self.advance_line_id:
            raise ValidationError(_("Select the advance line to apply."))

        if self.advance_line_id.partner_id != self.move_id.partner_id:
            raise ValidationError(
                _("The selected advance line belongs to a different partner.")
            )

        if not self.journal_id:
            raise ValidationError(_("Select a journal for the compensation entry."))

        if not self.journal_id.is_advance_journal:
            raise ValidationError(
                _("Journal '%s' is not configured for advance compensation.")
                % self.journal_id.display_name
            )

        self.invoice_line_id._validate_invoice_line()
        self.advance_line_id._validate_advance_line()

        invoice_residual = abs(self.invoice_line_id.amount_residual)
        advance_residual = abs(self.advance_line_id.amount_residual)
        if self.amount > invoice_residual:
            raise ValidationError(
                _("Amount %(amount).2f exceeds invoice residual %(residual).2f.")
                % {"amount": self.amount, "residual": invoice_residual}
            )

        if self.amount > advance_residual:
            raise ValidationError(
                _("Amount %(amount).2f exceeds advance residual %(residual).2f.")
                % {"amount": self.amount, "residual": advance_residual}
            )

    def _create_compensation_move(self):
        return self.env["account.move"].create(self._prepare_move_vals())

    def _prepare_move_vals(self):
        return {
            "move_type": "entry",
            "date": self.date,
            "journal_id": self.journal_id.id,
            "ref": _("Advance compensation for %s") % self.move_id.display_name,
            "line_ids": [
                (0, 0, self._prepare_compensation_line()),
                (0, 0, self._prepare_advance_line()),
            ],
        }

    def _prepare_compensation_line(self):
        is_in_invoice = self.move_id.move_type == "in_invoice"
        return {
            "name": _("Compensation for %s") % self.move_id.display_name,
            "partner_id": self.invoice_line_id.partner_id.id,
            "account_id": self.invoice_line_id.account_id.id,
            "debit": self.amount if is_in_invoice else 0,
            "credit": 0 if is_in_invoice else self.amount,
        }

    def _prepare_advance_line(self):
        is_in_invoice = self.move_id.move_type == "in_invoice"
        return {
            "name": _("Advance compensation from %s")
            % self.advance_line_id.move_id.name,
            "partner_id": self.advance_line_id.partner_id.id,
            "account_id": self.advance_line_id.account_id.id,
            "debit": 0 if is_in_invoice else self.amount,
            "credit": self.amount if is_in_invoice else 0,
        }

    def _get_compensation_lines(self, move):
        is_in_invoice = self.move_id.move_type == "in_invoice"
        compensation_line = move.line_ids.filtered(
            lambda line: (
                line.account_id == self.invoice_line_id.account_id
                and line.partner_id == self.move_id.partner_id
                and line.debit > 0
            )
            if is_in_invoice
            else (
                line.account_id == self.invoice_line_id.account_id
                and line.partner_id == self.move_id.partner_id
                and line.credit > 0
            )
        )[:1]
        advance_line = move.line_ids.filtered(
            lambda line: (
                line.account_id == self.advance_line_id.account_id
                and line.partner_id == self.move_id.partner_id
                and line.credit > 0
            )
            if is_in_invoice
            else (
                line.account_id == self.advance_line_id.account_id
                and line.partner_id == self.move_id.partner_id
                and line.debit > 0
            )
        )[:1]
        return compensation_line, advance_line

    def _process_reconciliation(self, move):
        if move.state != "posted":
            raise ValidationError(
                _("The compensation entry must be posted before reconciliation.")
            )

        compensation_line, advance_comp_line = self._get_compensation_lines(move)
        if not compensation_line or not advance_comp_line:
            raise ValidationError(
                _("Unable to identify generated compensation lines for reconciliation.")
            )

        lines_to_reconcile = (
            self.invoice_line_id
            + compensation_line
            + self.advance_line_id
            + advance_comp_line
        )
        try:
            (self.invoice_line_id + compensation_line).reconcile()
            (self.advance_line_id + advance_comp_line).reconcile()
        except Exception as err:
            lines_to_reconcile.remove_move_reconcile()
            raise ValidationError(
                _("Reconciliation failed for invoice '%(invoice)s': %(error)s")
                % {"invoice": self.move_id.display_name, "error": err}
            ) from err
        return True
