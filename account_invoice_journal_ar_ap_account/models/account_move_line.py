# Copyright 2026 Tecnativa - Adasat Torres
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    def _compute_account_id(self):
        super()._compute_account_id()
        for record in self.filtered(lambda line: line.display_type == "payment_term"):
            if record.move_id.journal_id.ar_ap_account_id:
                record.account_id = record.move_id.journal_id.ar_ap_account_id
        return
