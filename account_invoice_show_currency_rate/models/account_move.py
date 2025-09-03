# Copyright 2021 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    currency_rate_amount = fields.Float(
        string="Rate amount",
        compute="_compute_currency_rate_amount",
        digits=0,
    )
    show_currency_rate_amount = fields.Boolean(
        compute="_compute_show_currency_rate_amount", readonly=True
    )

    @api.depends(
        "state",
        "date",
        "line_ids.amount_currency",
        "line_ids.balance",
        "company_id",
        "currency_id",
        "show_currency_rate_amount",
    )
    def _compute_currency_rate_amount(self):
        """It's necessary to define value according to some cases:
        - Case A: Currency is equal to company currency (Value = 1)
        - Case B: Move exist previously (posted) and get real rate according to lines
        - Case C: Get expected rate (according to date) to show some value in creation.
        """
        self.currency_rate_amount = 1
        inverse = self.env.company.invoice_rate_display_type == "inverse_rate"
        for item in self.filtered("show_currency_rate_amount"):
            lines = item.line_ids.filtered(lambda x: abs(x.amount_currency) > 0)
            if item.state == "posted" and lines:
                amount_currency_positive = sum(
                    [abs(amc) for amc in lines.mapped("amount_currency")]
                )
                total_balance_positive = sum([abs(b) for b in lines.mapped("balance")])
                item.currency_rate_amount = (
                    (amount_currency_positive / total_balance_positive)
                    if not inverse
                    else (total_balance_positive / amount_currency_positive)
                )
            else:
                rates = item.currency_id._get_rates(item.company_id, item.date)
                item.currency_rate_amount = (
                    rates.get(item.currency_id.id)
                    if not inverse
                    else item.currency_id._convert(
                        1.0, item.company_id.currency_id, item.company_id, item.date
                    )
                )

    @api.depends("currency_id", "currency_id.rate_ids", "company_id")
    def _compute_show_currency_rate_amount(self):
        for item in self:
            item.show_currency_rate_amount = (
                item.currency_id and item.currency_id != item.company_id.currency_id
            )


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    @api.depends(
        "currency_id",
        "move_id.company_id",
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
