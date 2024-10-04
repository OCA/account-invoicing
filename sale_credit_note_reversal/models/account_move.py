# Copyright 2024 ForgeFlow (http://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
from odoo import models


class AccountMove(models.Model):
    _inherit = "account.move"

    def _reverse_moves(self, default_values_list=None, cancel=False):
        reversed_moves = super()._reverse_moves(
            default_values_list=default_values_list, cancel=cancel
        )
        for move in reversed_moves:
            if move.reversed_entry_id.move_type == "out_refund":
                # convert from entry to out_invoice
                move.move_type = "out_invoice"
        return reversed_moves
