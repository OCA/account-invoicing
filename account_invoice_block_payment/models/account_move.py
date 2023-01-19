# Copyright 2023 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo import _, fields, models
from odoo.exceptions import UserError


class AccountMove(models.Model):
    _inherit = "account.move"

    payment_blocked = fields.Boolean(
        help="if true, the payment of the invoice is blocked.",
    )

    def action_register_payment(self):
        error_msg = ""
        for move in self:
            if move.payment_blocked:
                error_msg += (
                    _("The payment on invoice {} is blocked.").format(move.name) + "\n"
                )
        if error_msg:
            raise UserError(error_msg)
        return super().action_register_payment()
