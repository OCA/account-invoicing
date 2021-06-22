# Copyright 2021 ForgeFlow (http://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
from odoo import fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    def _reverse_move_vals(self, default_values, cancel=True):
        # Set the sale_qty_not_to_reinvoice based on the boolean from the
        # reversal wizard
        move_vals = super(AccountMove, self)._reverse_move_vals(
            default_values, cancel=cancel
        )
        if self.env.context.get("sale_qty_not_to_reinvoice", False):
            for vals in move_vals["line_ids"]:
                vals[2].update({"sale_qty_not_to_reinvoice": True})
        return move_vals


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    sale_qty_not_to_reinvoice = fields.Boolean(
        string="Sale qty not to reinvoice",
        help="If marked, the quantity in this move line will not be considered "
        "as quantity to be reinvoiced in the related sales order line.",
    )
