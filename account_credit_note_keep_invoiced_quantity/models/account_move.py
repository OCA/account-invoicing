# Copyright 2023 Opener B.V. <stefan@opener.amsterdam>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import _, api, models
from odoo.exceptions import ValidationError


class AccountMove(models.Model):
    _inherit = "account.move"

    def _reverse_moves(self, default_values_list=None, cancel=False):
        """Update purchase order's invoice_ids with the reversals.

        It is a stored computed field and has to be triggered explicitely
        because we cannot add a recursive `api.depends`.
        """
        res = super()._reverse_moves(
            default_values_list=default_values_list, cancel=cancel
        )
        purchases = self.mapped("line_ids.purchase_order_id")
        moves = self
        while moves.mapped("reversed_entry_id"):
            moves = moves.mapped("reversed_entry_id")
            purchases |= moves.mapped("line_ids.purchase_order_id")
        purchases._compute_invoice()
        return res

    @api.constrains("reversed_entry_id")
    def _check_reversed_move_id_recursion(self):
        """Prevent the creation of recursion in the set of reversals.

        This would be quite disasterous in combination with the recursive
        queries in the sale and purchase compute methods.
        """
        for move in self:
            start = move
            while move.reversed_entry_id:
                if move.reversed_entry_id == start:
                    raise ValidationError(
                        _("You cannot create a recursive set of reversals")
                    )
                move = move.reversed_entry_id
