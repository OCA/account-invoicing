# Copyright 2021 ForgeFlow (http://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
from odoo import models


class AccountMove(models.Model):
    _inherit = "account.move"

    def copy(self, default=None):
        # Set the sale_qty_to_reinvoice based on the boolean from the
        # reversal wizard
        res = super().copy(default=default)
        sale_qty_to_reinvoice = self.env.context.get("sale_qty_to_reinvoice", False)
        res.line_ids.write({"sale_qty_to_reinvoice": sale_qty_to_reinvoice})
        return res
