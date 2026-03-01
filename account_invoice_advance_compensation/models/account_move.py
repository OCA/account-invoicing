# Copyright 2025, Kaynnan Lemes <kaynnan.lemes@escodoo.com.br>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class AccountMove(models.Model):
    _inherit = "account.move"

    advance_invoice = fields.Boolean(
        string="Has Advance Payments",
        compute="_compute_advance_invoice",
        help="Indicates whether this invoice has eligible advance payments available",
    )

    @api.depends(
        "partner_id",
        "move_type",
        "line_ids.account_id.account_type",
        "line_ids.amount_residual",
    )
    def _compute_advance_invoice(self):
        """Compute whether advance payments are available for this invoice.

        This method checks if there are any eligible advance payments that can be
        used to compensate this invoice. It processes invoices by partner for
        better performance.
        """
        prepayment_account_type = "asset_prepayments"

        # Reset all to False first
        self.advance_invoice = False

        # Only process invoices with partners
        invoices = self.filtered(lambda m: m.partner_id and m.is_invoice())

        # Process by partner for better performance
        for partner in invoices.partner_id:
            partner_invoices = invoices.filtered_domain(
                [("partner_id", "=", partner.id)]
            )
            domain = self._get_advance_domain(partner, prepayment_account_type)
            has_advance = bool(self.env["account.move.line"].search(domain, limit=1))

            # Set value for all invoices of this partner
            partner_invoices.advance_invoice = has_advance

    def _get_advance_domain(self, partner, account_type):
        """Build domain to find advance payments for a partner.

        Args:
            partner: Partner to find advance payments for
            account_type: Account type to filter by

        Returns:
            Domain to search for advance payments
        """
        return [
            ("move_id.payment_state", "=", "paid"),
            ("partner_id", "=", partner.id),
            ("account_id.account_type", "=", account_type),
            ("account_id.reconcile", "=", True),
            ("amount_residual", "!=", 0),
        ]

    def action_open_advance_compensation(self):
        """Open the advance compensation wizard.

        Returns:
            Action to open the compensation wizard
        """
        self.ensure_one()
        self._validate_advance_compensation()

        return {
            "name": _("Compensate Advance"),
            "type": "ir.actions.act_window",
            "res_model": "account.invoice.advance.compensation.wizard",
            "view_mode": "form",
            "target": "new",
            "context": {
                "default_move_id": self.id,
                "default_move_type": self.move_type,
            },
        }

    def _validate_advance_compensation(self):
        """Validate if advance compensation is possible.

        Raises:
            ValidationError: If advance compensation is not possible
        """
        if not self.partner_id:
            raise ValidationError(_("Partner is required for advance compensation."))

        if not self.is_invoice():
            raise ValidationError(_("Only invoices can be compensated with advances."))

        if not self.advance_invoice:
            raise ValidationError(
                _("No eligible advance payments available for this invoice.")
            )
