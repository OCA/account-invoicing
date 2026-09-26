# © 2026 Solvos Consultoría Informática (<http://www.solvos.es>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class AccountMove(models.Model):
    _inherit = "account.move"

    def _reverse_moves(self, default_values_list=None, cancel=False):
        # Set the purchase_qty_to_reinvoice based on the boolean from the
        # reversal wizard
        move_vals = super()._reverse_moves(default_values_list, cancel=cancel)
        if self.env.context.get("purchase_qty_to_reinvoice", False):
            for vals in move_vals["line_ids"]:
                vals.update({"purchase_qty_to_reinvoice": True})
        return move_vals
