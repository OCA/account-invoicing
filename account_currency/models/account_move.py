# Copyright (C) 2025 Cetmix OÜ
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class AccountMove(models.Model):
    _inherit = "account.move"

    @api.depends("journal_id", "statement_line_id")
    def _compute_currency_id(self):
        result = super()._compute_currency_id()
        company = self.env.company
        for invoice in self.filtered(
            lambda rec: rec.move_type in ["out_invoice", "in_invoice"]
        ):
            invoice.currency_id = (
                company.default_account_currency_id or invoice.currency_id
            )
        return result
