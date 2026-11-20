# Copyright 2024 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class AccountPayment(models.Model):
    _inherit = "account.payment"

    def action_post(self):
        res = super().action_post()
        for payment in self:
            if payment.move_id.state == "draft":
                # ``account.payment.write()`` normally re-posts a draft
                # ``move_id`` as a side effect of the state change triggered
                # by ``super().action_post()``. That side effect can be
                # short-circuited by other modules overriding
                # ``account.move.action_post()``/``_post()``, leaving the
                # move in draft and the reconciliation below silently
                # skipped. Post it explicitly instead of relying on it.
                payment.move_id.action_post()
            invoices = payment.invoice_ids.filtered(
                lambda line: line.payment_state != "paid"
                and line.state == "posted"
                and line.move_type != "entry"
            )
            if not invoices or not payment.move_id:
                continue
            lines = (invoices + payment.move_id).mapped("line_ids")
            reconcile_lines = lines.filtered(
                lambda line: line.account_id.reconcile
                and not line.reconciled
                and line.account_id.account_type
                in (
                    "asset_receivable",
                    "liability_payable",
                )
            )
            if reconcile_lines:
                reconcile_lines.reconcile()
        return res
