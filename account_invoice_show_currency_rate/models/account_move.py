# Copyright 2021 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class AccountMove(models.Model):
    _inherit = "account.move"

    @api.depends(
        "currency_id",
        "company_currency_id",
        "company_id",
        "invoice_date",
        "state",
        "line_ids.amount_currency",
        "line_ids.balance",
    )
    def _compute_invoice_currency_rate(self):
        # If move is posted, get rate based on line amount
        res = super()._compute_invoice_currency_rate()
        for move in self:
            lines = move.line_ids.filtered(lambda x: abs(x.amount_currency) > 0)
            if move.state != "posted" or not lines or not move.currency_id:
                continue
            amount_currency_positive = sum(
                [abs(amc) for amc in lines.mapped("amount_currency")]
            )
            total_balance_positive = sum([abs(b) for b in lines.mapped("balance")])
            move.invoice_currency_rate = (
                amount_currency_positive / total_balance_positive
            )
        return res


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    @api.depends(
        "currency_id",
        "company_id",
        "move_id.invoice_currency_rate",
        "move_id.date",
        "move_id.state",
        "amount_currency",
        "balance",
    )
    def _compute_currency_rate(self):
        # If move is posted, get rate based on line amount
        res = super()._compute_currency_rate()
        for line in self:
            if line.move_id.state != "posted" or not line.amount_currency:
                continue
            line.currency_rate = (
                abs(line.amount_currency) / abs(line.balance) if line.balance else 0
            )
        return res
