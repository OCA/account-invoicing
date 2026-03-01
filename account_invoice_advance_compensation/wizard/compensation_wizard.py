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
        """Compute the currency based on the selected journal."""
        for wizard in self:
            wizard.currency_id = (
                wizard.journal_id.currency_id
                or wizard.journal_id.company_id.currency_id
            )

    @api.depends("move_id", "move_id.partner_id", "move_id.move_type")
    def _compute_available_advance_lines(self):
        """Compute available advance lines for the current invoice."""
        for wizard in self:
            wizard.available_advance_line_ids = wizard._get_available_advance_lines()

    @api.depends("advance_line_id")
    def _compute_advance_balance(self):
        """Compute the available balance in the selected advance line."""
        for wizard in self:
            wizard.advance_balance = (
                abs(wizard.advance_line_id.amount_residual)
                if wizard.advance_line_id
                else 0
            )

    @api.onchange("invoice_line_id", "advance_line_id")
    def _onchange_invoice_line_id(self):
        """Set default amount based on invoice line residual."""
        if self.invoice_line_id and self.advance_line_id:
            self.amount = min(
                abs(self.invoice_line_id.amount_residual),
                abs(self.advance_line_id.amount_residual),
            )

    def action_confirm_compensation(self):
        """Create compensation journal entry and reconcile.

        Returns:
            Action to open the created journal entry
        """
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
        """Get available advance lines for current invoice.

        Returns:
            Recordset of available advance lines
        """
        empty = self.env["account.move.line"]
        move = self.move_id

        base_domain = [
            ("move_id.payment_state", "=", "paid"),
            ("partner_id", "=", move.partner_id.id),
            ("account_id.account_type", "=", "asset_prepayments"),
            ("account_id.reconcile", "=", True),
            ("amount_residual", "!=", 0),
        ]

        sign_domain = (
            (move.move_type == "in_invoice") and [("amount_residual", ">", 0)]
        ) or [("amount_residual", "<", 0)]

        domain = base_domain + sign_domain

        return (
            move and move.partner_id and self.env["account.move.line"].search(domain)
        ) or empty

    def _raise_validation(self, message):
        raise ValidationError(message)

    def _require(self, condition, message):
        return condition or self._raise_validation(message)

    def _validate_compensation(self):
        """Validate compensation parameters.

        Raises:
            ValidationError: If any validation fails
        """
        self._require(self.amount > 0, _("Compensation amount must be positive."))
        self._require(self.move_id, _("The invoice is required."))
        self._require(
            self.move_id.state == "posted",
            _("Only posted invoices can be compensated."),
        )
        self._require(
            self.move_id.is_invoice(),
            _("Only invoices can be compensated with advances."),
        )

        self._require(
            self.invoice_line_id,
            _("Please select an invoice line to compensate."),
        )

        self._require(
            self.advance_line_id,
            _("Please select an advance line to use."),
        )
        self._require(
            self.invoice_line_id.move_id == self.move_id,
            _("Selected invoice line does not belong to this invoice."),
        )

        self._require(
            self.amount <= abs(self.invoice_line_id.amount_residual),
            _("Compensation amount cannot exceed the invoice line residual amount."),
        )

        self._require(
            self.amount <= abs(self.advance_line_id.amount_residual),
            _("Compensation amount cannot exceed the advance line balance."),
        )

    def _create_compensation_move(self):
        """Create the compensation journal entry.

        Returns:
            Created journal entry
        """
        return self.env["account.move"].create(self._prepare_move_vals())

    def _prepare_move_vals(self):
        """Prepare values for the compensation journal entry.

        Returns:
            Values for the journal entry creation
        """
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
        """Prepare the compensation line for the journal entry.

        Returns:
            Values for the compensation line
        """
        is_in_invoice = self.invoice_line_id.move_id.move_type == "in_invoice"
        return {
            "name": _("Compensation for %s") % self.invoice_line_id.move_id.name,
            "partner_id": self.invoice_line_id.partner_id.id,
            "account_id": self.invoice_line_id.account_id.id,
            "debit": self.amount if is_in_invoice else 0,
            "credit": 0 if is_in_invoice else self.amount,
        }

    def _prepare_advance_line(self):
        """Prepare the advance line for the journal entry.

        Returns:
            Values for the advance line
        """
        is_in_invoice = self.invoice_line_id.move_id.move_type == "in_invoice"
        return {
            "name": _("Advance compensation from %s")
            % self.advance_line_id.move_id.name,
            "partner_id": self.advance_line_id.partner_id.id,
            "account_id": self.advance_line_id.account_id.id,
            "debit": 0 if is_in_invoice else self.amount,
            "credit": self.amount if is_in_invoice else 0,
        }

    def _process_reconciliation(self, move):
        """Process the reconciliation between the invoice and advance lines.

        Args:
            move: The compensation journal entry to reconcile

        Returns:
            True if reconciliation is successful

        Raises:
            ValidationError: If reconciliation fails
        """
        if move.state != "posted":
            raise ValidationError(_("Cannot reconcile unposted journal entry."))

        compensation_line = move.line_ids.filtered(
            lambda line: line.account_id == self.invoice_line_id.account_id
        )[:1]
        advance_comp_line = move.line_ids.filtered(
            lambda line: line.account_id == self.advance_line_id.account_id
        )[:1]

        self._require(
            compensation_line and advance_comp_line,
            _("Could not identify compensation lines in the generated entry."),
        )

        (self.invoice_line_id + compensation_line).reconcile()
        (self.advance_line_id + advance_comp_line).reconcile()
        return True
