# Copyright 2023 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, models
from odoo.exceptions import UserError


class AccountPaymentRegister(models.TransientModel):
    _inherit = "account.payment.register"

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        if self._context.get("active_model") == "account.move":
            moves = self.env["account.move"].browse(self._context.get("active_ids", []))
        elif self._context.get("active_model") == "account.move.line":
            moves = (
                self.env["account.move.line"]
                .browse(self._context.get("active_ids", []))
                .mapped("move_id")
            )
        # Check manual currency
        if len(set(moves.mapped("manual_currency"))) != 1:
            raise UserError(
                _(
                    "You can only register payments for moves with the same manual currency."
                )
            )
        return res

    def _init_payments(self, to_process, edit_mode=False):
        payments = super()._init_payments(to_process, edit_mode)
        if self._context.get("active_model") == "account.move":
            for vals in to_process:
                lines = vals["to_reconcile"]
                payment = vals["payment"]
                origin_move = lines.mapped("move_id")
                # Not allow group payments for case manual currency
                if (
                    self.group_payment
                    and len(origin_move) != 1
                    and len({move.manual_currency_rate for move in origin_move}) != 1
                ):
                    raise UserError(
                        _(
                            "You can't register a payment for invoices "
                            "belong to multiple manual currency rate."
                        )
                    )
                if all(move.manual_currency for move in origin_move):
                    payment.move_id.write(
                        {
                            "manual_currency": origin_move[0].manual_currency,
                            "type_currency": origin_move[0].type_currency,
                            "manual_currency_rate": origin_move[0].manual_currency_rate,
                        }
                    )
                    payment.move_id.with_context(
                        check_move_validity=False
                    ).line_ids._onchange_amount_currency()
        return payments
