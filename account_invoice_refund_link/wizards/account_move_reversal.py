# Copyright 2020 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class AccountMoveReversal(models.TransientModel):
    _inherit = "account.move.reversal"

    def reverse_moves(self):
        """
        Only link invoice lines with theirs original lines when the reversal
        move has been done from reversal wizard.
        """
        return super(
            AccountMoveReversal, self.with_context(link_origin_line=True)
        ).reverse_moves()
