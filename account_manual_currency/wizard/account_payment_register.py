# Copyright 2023 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class AccountPaymentRegister(models.TransientModel):
    _inherit = "account.payment.register"

    currency_diff = fields.Boolean(
        compute="_compute_currency_diff",
        store=True,
    )
    manual_currency = fields.Boolean()
    type_currency = fields.Selection(
        selection=lambda self: self.line_ids.move_id._get_label_currency_name(),
    )
    manual_currency_rate = fields.Float(
        digits="Manual Currency",
        help="Set new currency rate to apply on the invoice\n."
        "This rate will be taken in order to convert amounts between the "
        "currency on the purchase order and last currency",
    )

    @api.depends("currency_id")
    def _compute_currency_diff(self):
        for rec in self:
            rec.currency_diff = rec.company_currency_id != rec.currency_id

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
        res["manual_currency"] = moves.mapped("manual_currency")[0]
        if len(list(set(moves.mapped("manual_currency_rate")))) == 1:
            res["manual_currency_rate"] = moves.mapped("manual_currency_rate")[0]
        if len(list(set(moves.mapped("type_currency")))) == 1:
            res["type_currency"] = moves.mapped("type_currency")[0]
        return res

    def _init_payments(self, to_process, edit_mode=False):
        """Update currency rate on move line payment"""
        payments = super()._init_payments(to_process, edit_mode)
        if self._context.get("active_model") == "account.move" and self.manual_currency:
            for vals in to_process:
                payment = vals["payment"]
                payment.move_id.write(
                    {
                        "manual_currency": self.manual_currency,
                        "type_currency": self.type_currency,
                        "manual_currency_rate": self.manual_currency_rate,
                    }
                )
                payment.move_id.with_context(
                    check_move_validity=False
                ).line_ids._onchange_amount_currency()
        return payments
