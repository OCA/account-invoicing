# Copyright 2017-2018 Vauxoo
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    custom_rate = fields.Float(
        digits=(12, 6),
        default=1,
        store=True,
        readonly=False,
        compute="_compute_currency_change_rate",
        help="Set new currency rate to apply on the invoice.\n"
        "This rate will be taken in order to convert amounts between the "
        "currency on the invoice and last currency",
    )
    original_currency_id = fields.Many2one(
        "res.currency",
        help="Store the original currency when the invoice is created or the "
        "conversion is called for the first time. "
        "This is used to calculate conversion from this currency.",
    )
    is_original_currency = fields.Boolean(
        compute="_compute_is_original_currency",
        help="Check if current currency is the original currency. "
        "This is used to hide custom rate field in the form view.",
    )

    @api.model
    def create(self, values):
        values.setdefault("original_currency_id", values.get("currency_id"))
        return super().create(values)

    def action_account_change_currency(self):
        """
        This method convert the original price unit from the original
        currency when the invoice was created to the current currency
        using the custom rate and recompute all taxes.
        """
        today = fields.Date.context_today(self)
        invoices = self.filtered(lambda x: x.state == "draft").with_context(
            check_move_validity=False,
        )
        for invoice in invoices:
            if not invoice.original_currency_id:
                invoice.write({"original_currency_id": invoice.currency_id})
                invoice.invoice_line_ids._set_original_price_unit()
            invoice_date = invoice.invoice_date or today
            to_currency = invoice.currency_id
            context = {"custom_rate": invoice.custom_rate, "to_currency": to_currency}
            original_currency = invoice.original_currency_id.with_context(**context)
            for line in invoice.invoice_line_ids:
                line.price_unit = original_currency._convert(
                    line.original_price_unit,
                    to_currency,
                    invoice.company_id,
                    invoice_date,
                )
            invoice._recompute_dynamic_lines(recompute_all_taxes=True)

    @api.depends("company_id", "currency_id", "invoice_date")
    def _compute_currency_change_rate(self):
        """
        Compute the custom rate from the original currency when the invoice
        was created to the current currency. The custom rate field is
        editable, but it will not change if custom rate is zero or the
        current currency and the original currency are the same
        """
        for invoice in self:
            if not invoice.currency_id or not invoice.company_id:
                invoice.custom_rate = 1.0
                continue
            date = invoice.invoice_date or fields.Date.context_today(invoice)
            from_currency = invoice.original_currency_id or invoice.currency_id
            invoice.custom_rate = from_currency._get_conversion_rate(
                from_currency,
                invoice.currency_id,
                invoice.company_id,
                date,
            )

    @api.depends("currency_id", "original_currency_id")
    def _compute_is_original_currency(self):
        """
        Compute if the current currency and the original currency
        are the same. The is_original_currency field is used in the
        view to hide the custom_rate field.
        """
        for invoice in self:
            invoice.is_original_currency = (
                invoice.currency_id == invoice.original_currency_id
            )
