# Copyright 2020 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class AccountPayment(models.Model):
    _inherit = "account.payment"

    def post(self):
        res = super().post()
        active_ids = self._context.get("active_ids", False)
        move_ids = self.env["account.move"].browse(active_ids)
        warranty_moves = move_ids.mapped("warranty_move_ids").filtered(
            lambda l: l.is_return is False
        )
        if warranty_moves:
            warranty_moves.write({"is_return": True})
        return res
