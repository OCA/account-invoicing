# Copyright 2026, Escodoo - https://www.escodoo.com.br
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, models
from odoo.exceptions import ValidationError


class AccountInvoiceAdvanceCompensationWizard(models.TransientModel):
    _inherit = "account.invoice.advance.compensation.wizard"

    def _validate_compensation(self):
        if not self.env.context.get("skip_advance_journal_check"):
            return super()._validate_compensation()

        self.ensure_one()
        if self.amount <= 0:
            raise ValidationError(_("The compensation amount must be positive."))

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
