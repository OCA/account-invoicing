from collections import defaultdict

from odoo import Command, _, models
from odoo.exceptions import AccessError

TYPE_REVERSE_MAP = {
    "entry": "entry",
    "out_invoice": "out_refund",
    "out_refund": "entry",
    "in_invoice": "in_refund",
    "in_refund": "entry",
    "out_receipt": "entry",
    "in_receipt": "entry",
}


class AccountMove(models.Model):
    _inherit = "account.move"

    def _ar_ap_post(self, soft=True):
        if not self.env.su and not (
            self.env.user.has_group("account.group_account_invoice")
            or self.env.user.has_group(
                "account_user_group.group_account_account_receivable"
            )
            or self.env.user.has_group(
                "account_user_group.group_account_account_payable"
            )
        ):
            raise AccessError(_("You don't have the access rights to post an invoice."))
        else:
            if soft:
                self.sudo()._post(soft=True)
            else:
                self.sudo()._post(soft=False)

    def action_post(self):
        moves_with_payments = self.filtered("payment_id")
        other_moves = self - moves_with_payments
        if moves_with_payments:
            moves_with_payments.payment_id.action_post()
        if other_moves:
            other_moves._ar_ap_post(soft=False)
        return False

    def _reverse_moves(self, default_values_list=None, cancel=False):
        if not default_values_list:
            default_values_list = [{} for move in self]

        if cancel:
            lines = self.mapped("line_ids")
            # Avoid maximum recursion depth.
            if lines:
                lines.remove_move_reconcile()

        reverse_moves = self.env["account.move"]
        for move, default_values in zip(self, default_values_list):
            default_values.update(
                {
                    "move_type": TYPE_REVERSE_MAP[move.move_type],
                    "reversed_entry_id": move.id,
                }
            )
            reverse_moves += move.with_context(
                move_reverse_cancel=cancel,
                include_business_fields=True,
                skip_invoice_sync=bool(move.tax_cash_basis_origin_move_id),
            ).copy(default_values)

        reverse_moves.with_context(skip_invoice_sync=cancel).write(
            {
                "line_ids": [
                    Command.update(
                        line.id,
                        {
                            "balance": -line.balance,
                            "amount_currency": -line.amount_currency,
                        },
                    )
                    for line in reverse_moves.line_ids
                    if line.move_id.move_type == "entry" or line.display_type == "cogs"
                ]
            }
        )

        # Reconcile moves together to cancel the previous one.
        if cancel:
            reverse_moves.with_context(move_reverse_cancel=cancel)._ar_ap_post(
                soft=False
            )
            for move, reverse_move in zip(self, reverse_moves):
                group = defaultdict(list)
                for line in (move.line_ids + reverse_move.line_ids).filtered(
                    lambda l: not l.reconciled
                ):
                    group[(line.account_id, line.currency_id)].append(line.id)
                for (account, _dummy), line_ids in group.items():
                    if account.reconcile or account.account_type in (
                        "asset_cash",
                        "liability_credit_card",
                    ):
                        self.env["account.move.line"].browse(line_ids).with_context(
                            move_reverse_cancel=cancel
                        ).reconcile()

        return reverse_moves
