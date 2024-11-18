# Copyright 2021 Tecnativa - Víctor Martínez
# Copyright 2024 ForgeFlow S.L. (http://www.forgeflow.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    currency_rate_amount = fields.Float(
        string="Rate amount", compute="_compute_currency_rate_amount", digits=0,
    )
    show_currency_rate_amount = fields.Boolean(
        compute="_compute_show_currency_rate_amount", readonly=True
    )

    @api.depends(
        "state",
        "date",
        "amount_total_company_signed",
        "amount_total_signed",
        "company_id",
        "currency_id",
        "show_currency_rate_amount",
    )
    def _compute_currency_rate_amount(self):
        """ It's necessary to define value according to some cases:
        - Case A: Currency is equal to company currency (Value = 1)
        - Case B: Invoice exist previously (confirmed) and get real rate
        according to amount
        - Case C: Get expected rate (according to date)
        to show some value in creation.
        """
        for item in self:
            item.currency_rate_amount = 1
            if not item.show_currency_rate_amount:
                continue
            if item.state == 'open':
                item.currency_rate_amount = item.currency_id.round(
                    item.amount_total_signed / item.amount_total_company_signed
                )
            else:
                date = item.date or fields.Date.today()
                item.currency_rate_amount = item.currency_id.with_context(
                    date=date).rate

    @api.depends("currency_id", "currency_id.rate_ids", "company_id")
    def _compute_show_currency_rate_amount(self):
        for item in self:
            item.show_currency_rate_amount = (
                item.currency_id and item.currency_id != item.company_id.currency_id
            )
