# Copyright 2025, Kaynnan Lemes <kaynnan.lemes@escodoo.com.br>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, models
from odoo.exceptions import ValidationError
from odoo.tools.misc import formatLang


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    def name_get(self):
        """Custom display name for move lines based on context.

        Returns:
            List of tuples containing (id, display_name)
            for each record. The display name format depends on the context:
            - For advance payments (context 'advance_id_name_get')
            - For invoice lines (context 'line_id_name_get')
            - Default name_get behavior otherwise
        """
        if self.env.context.get("advance_id_name_get"):
            return self._get_advance_display_name()
        if self.env.context.get("line_id_name_get"):
            return self._get_invoice_line_display_name()
        return super().name_get()

    def _get_advance_display_name(self):
        """Format display name for advance payment lines.

        Format: Name | Date | Total Amount | Balance

        Returns:
            List of tuples containing (id, display_name)
            for each advance payment line
        """
        result = []
        for line in self:
            name_parts = [
                line.name,
                _("Date: %s") % line.move_id.date.strftime("%x"),
                _("Balance: %s")
                % formatLang(
                    self.env, abs(line.amount_residual), currency_obj=line.currency_id
                ),
            ]
            result.append((line.id, " | ".join(filter(None, name_parts))))
        return result

    def _get_invoice_line_display_name(self):
        """Format display name for invoice lines.

        Format: Name | Due Date | Balance Amount

        Returns:
            List of tuples containing (id, display_name)
            for each invoice line
        """
        result = []
        for line in self:
            name_parts = [
                line.name or line.move_id.name,
                _("Date: %s")
                % (line.date_maturity.strftime("%x") if line.date_maturity else ""),
                _("Balance: %s")
                % formatLang(
                    self.env, abs(line.balance), currency_obj=line.currency_id
                ),
            ]
            result.append((line.id, " | ".join(filter(None, name_parts))))
        return result

    def _validate_advance_line(self):
        """Validate if the line can be used as an advance payment.

        Raises:
            ValidationError: If the line cannot be used as an advance payment
        """
        if not self.account_id.account_type == "asset_prepayments":
            raise ValidationError(
                _("Only prepayment accounts can be used as advances.")
            )

        if not self.account_id.reconcile:
            raise ValidationError(_("Advance account must be reconcilable."))

        if self.amount_residual == 0:
            raise ValidationError(_("Advance line must have a residual amount."))

    def _raise_validation(self, message):
        raise ValidationError(message)

    def _require(self, condition, message):
        return condition or self._raise_validation(message)

    def _validate_invoice_line(self):
        """Validate if the line can be compensated.

        Raises:
            ValidationError: If the line cannot be compensated
        """
        self._require(
            self.move_id.is_invoice(),
            _("Only invoice lines can be compensated."),
        )

        self._require(
            self.amount_residual != 0,
            _("Invoice line must have a residual amount."),
        )
