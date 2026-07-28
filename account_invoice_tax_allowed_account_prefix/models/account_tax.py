# Copyright 2026 ACSONE SA/NV,BCIM
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class AccountTax(models.Model):

    _inherit = "account.tax"

    allowed_account_prefix = fields.Char(
        string="Allowed Account Prefixes",
        help=(
            "Comma-separated list of account code prefixes. "
            "If set, this tax can only be used on invoice lines whose "
            "account code starts with one of these prefixes.\n\n"
            "Examples:\n"
            "- '60' → accounts starting with 60\n"
            "- '60,61' → accounts starting with 60 or 61\n"
            "- leave empty → tax allowed for all accounts"
        ),
    )

    def _get_allowed_prefixes(self):
        """return list of normalized prefixes"""
        self.ensure_one()
        if not self.allowed_account_prefix:
            return []
        return [p.strip() for p in self.allowed_account_prefix.split(",") if p.strip()]

    def _is_allowed_for_account(self, account, strict=False):
        """check if tax is allowed for the given account"""
        self.ensure_one()
        if not account or not account.code:
            return True
        prefixes = self._get_allowed_prefixes()
        if not prefixes:
            return not strict
        return any(account.code.startswith(prefix) for prefix in prefixes)

    def _filter_allowed_for_account(self, account, strict=False):
        """filter taxes allowed for the given account"""
        return self.filtered(
            lambda t: t._is_allowed_for_account(account, strict=strict)
        )
