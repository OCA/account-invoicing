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
        "invoice_date",
        "company_id",
        "currency_id",
        "show_currency_rate_amount",
    )
    def _compute_currency_rate_amount(self):
        self.currency_rate_amount = 1
        for item in self.filtered("show_currency_rate_amount"):
            date = item.invoice_date or item.date
            rates = item.currency_id._get_rates(item.company_id, date)
            item.currency_rate_amount = rates.get(item.currency_id.id)

    @api.depends("currency_id", "currency_id.rate_ids", "company_id")
    def _compute_show_currency_rate_amount(self):
        for item in self:
            item.show_currency_rate_amount = (
                item.currency_id and item.currency_id != item.company_id.currency_id
            )
