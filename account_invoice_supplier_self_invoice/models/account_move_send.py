# Copyright 2026 - Moduon
# License AGPL-3.0 or later (https://www.gnuorg/licenses/agpl.html).

from odoo import api, models


class AccountMoveSend(models.AbstractModel):
    _inherit = "account.move.send"

    @api.model
    def _check_move_constrains(self, moves):
        if all(
            move.is_purchase_document(include_receipts=False)
            and move.self_invoice_number
            for move in moves
        ):
            return  # All moves are self invoices. Skip completely the check
        return super()._check_move_constrains(moves)
