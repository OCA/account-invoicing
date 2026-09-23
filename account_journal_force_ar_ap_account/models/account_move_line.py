# Copyright 2026 Tecnativa - Adasat Torres
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    def _compute_account_id(self):
        res = super()._compute_account_id()
        for line in self.filtered(
            lambda line: line.display_type == "payment_term"
            and line.move_id.journal_id.ar_ap_account_id
        ):
            line.account_id = line.move_id.journal_id.ar_ap_account_id
        return res
