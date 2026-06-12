# Copyright 2025, Kaynnan Lemes <kaynnan.lemes@escodoo.com.br>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, models
from odoo.exceptions import ValidationError
from odoo.tools.misc import formatLang


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    def name_get(self):
        if self.env.context.get("advance_id_name_get"):
            return self._get_advance_display_name()
        if self.env.context.get("line_id_name_get"):
            return self._get_invoice_line_display_name()
        return [(line.id, line.display_name) for line in self]

    def _get_advance_display_name(self):
        result = []
        for line in self:
            name_parts = [
                line.name,
                _("Date: %s") % (line.move_id.date or ""),
                _("Balance: %s")
                % formatLang(
                    self.env, abs(line.amount_residual), currency_obj=line.currency_id
                ),
            ]
            result.append((line.id, " | ".join(filter(None, name_parts))))
        return result

    def _get_invoice_line_display_name(self):
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
        self.ensure_one()
        if self.account_id.account_type != "asset_prepayments":
            raise ValidationError(
                _(
                    "Line '%(line)s' uses account '%(account)s'. "
                    "Only prepayment accounts are valid for advance compensation."
                )
                % {
                    "line": self.display_name,
                    "account": self.account_id.display_name,
                }
            )

        if not self.account_id.reconcile:
            raise ValidationError(
                _("Account '%s' must allow reconciliation.")
                % self.account_id.display_name
            )

        if self.amount_residual == 0:
            raise ValidationError(
                _("Line '%(line)s' has no open residual amount to be compensated.")
                % {"line": self.display_name}
            )

    def _validate_invoice_line(self):
        self.ensure_one()
        if not self.move_id.is_invoice(include_receipts=False):
            raise ValidationError(
                _("Line '%s' does not belong to an invoice or bill.")
                % self.display_name
            )

        if self.account_id.account_type not in (
            "asset_receivable",
            "liability_payable",
        ):
            raise ValidationError(
                _(
                    "Line '%(line)s' uses account '%(account)s'. "
                    "Only receivable or payable lines can be compensated."
                )
                % {
                    "line": self.display_name,
                    "account": self.account_id.display_name,
                }
            )

        if self.amount_residual == 0:
            raise ValidationError(
                _("Line '%s' has no open residual amount.") % self.display_name
            )
