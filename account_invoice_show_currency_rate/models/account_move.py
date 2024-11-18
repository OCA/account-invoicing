# Copyright 2021 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    currency_rate_amount = fields.Float(
        string="Rate amount", compute="_compute_currency_rate_amount", digits=0,
    )

    @api.depends(
        "move_id.state",
        "move_id.date",
        "amount_currency",
        "balance",
        "move_id.company_id",
        "currency_id",
    )
    def _compute_currency_rate_amount(self):
        """ It's necessary to define value according to some cases:
        - Case A: Currency is equal to company currency (Value = 1)
        - Case B: Move exist previously (posted)
        and get real rate according to lines
        - Case C: Get expected rate (according to date)
        to show some value in creation.
        """
        for item in self:
            item.currency_rate_amount = 1
            if (
                not item.currency_id
                or item.currency_id == item.move_id.company_id.currency_id
            ):
                continue
            amount_currency = abs(item.amount_currency)
            if item.move_id.state == "posted" and amount_currency > 0:
                item.currency_rate_amount = item.currency_id.round(
                    amount_currency / abs(item.balance)
                )
            else:
                date = item.move_id.date or fields.Date.today()
                item.currency_rate_amount = item.currency_id.with_context(
                    date=date).rate
