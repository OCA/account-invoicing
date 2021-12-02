# Copyright 2021 Camptocamp (https://www.camptocamp.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import models


class AccountMoveReversal(models.TransientModel):
    _inherit = "account.move.reversal"

    def reverse_moves(self):
        # Add flag to be intercepted by `account.move`'s :meth:`copy_data`
        self_ctx = self.with_context(propagate_ref=True)
        return super(AccountMoveReversal, self_ctx).reverse_moves()
