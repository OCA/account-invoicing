# Copyright 2025 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models


class AccountMove(models.Model):
    _inherit = "account.move"

    def _compute_payment_reference(self):
        for move in self.filtered(
            lambda m: (
                m.state == "posted"
                and m.move_type == "out_invoice"
                and not m.payment_reference
            )
        ):
            for tx in move.transaction_ids:
                if tx.state != "done":
                    continue
                move.payment_reference = tx.reference
                break
        return super()._compute_payment_reference()
