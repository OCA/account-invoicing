# Copyright 2026 Camptocamp SA (https://www.camptocamp.com).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class AccountTax(models.Model):
    _inherit = "account.tax"

    currency_id = fields.Many2one(
        "res.currency",
        help="When set, the fixed amount is expressed in this currency and "
        "will be converted to the document currency at invoice time. "
        "Leave empty for the standard behavior (amount in document currency).",
    )
    currency_rate = fields.Float(
        compute="_compute_currency_rate",
        help="Conversion rate from the tax currency to the company currency.",
    )

    @api.depends_context("document_date")
    @api.depends("currency_id", "company_id.currency_id")
    def _compute_currency_rate(self):
        date = self.env.context.get("document_date") or fields.Date.today()
        for tax in self:
            if not tax.currency_id or tax.currency_id == tax.company_id.currency_id:
                tax.currency_rate = 1.0
            else:
                tax.currency_rate = self.env["res.currency"]._get_conversion_rate(
                    tax.currency_id,
                    tax.company_id.currency_id,
                    tax.company_id,
                    date,
                )

    def _eval_tax_amount_convert_currency(self, amount):
        """Convert the tax amount from the tax currency to the document currency.

        [!] Mirror of the same method in account_tax.js.
        PLZ KEEP BOTH METHODS CONSISTENT WITH EACH OTHERS.

        We use a helper field `account.tax.currency_rate` to ease the conversion
        in the JS side. We use it here as well to keep both methods consistent.

        :param amount: The tax amount to convert.
        :return: The converted amount.
        """
        self.ensure_one()
        document_currency = self.env.context.get("document_currency")
        document_rate = self.env.context.get("document_rate")
        # When called outside a document context (e.g. _get_tax_details
        # directly), there is no conversion to apply.
        if not document_currency:
            return amount
        # If the currency already matches, skip the conversion
        if self.currency_id == document_currency:
            return amount
        # Convert: tax currency → company currency → document currency
        return amount * self.currency_rate * document_rate

    def _eval_tax_amount_fixed_amount(self, batch, raw_base, evaluation_context):
        res = super()._eval_tax_amount_fixed_amount(batch, raw_base, evaluation_context)
        if self.amount_type == "fixed" and self.currency_id:
            return self._eval_tax_amount_convert_currency(res)
        return res

    @api.model
    def _prepare_base_line_for_taxes_computation(self, record, **kwargs):
        # OVERRIDE to add the document date to the base line
        base_line = super()._prepare_base_line_for_taxes_computation(record, **kwargs)
        base_line["date"] = self._get_base_line_field_value_from_record(
            record, "date", kwargs, fields.Date.today()
        )
        return base_line

    @api.model
    def _add_tax_details_in_base_line(self, base_line, company, rounding_method=None):
        # OVERRIDE to add the document currency, rate and date to the context
        rate = base_line.get("rate", 1.0)
        currency_id = base_line.get("currency_id")
        date = base_line.get("date")
        base_line["tax_ids"] = base_line["tax_ids"].with_context(
            document_currency=currency_id,
            document_rate=rate,
            document_date=date,
        )
        return super()._add_tax_details_in_base_line(
            base_line, company, rounding_method=rounding_method
        )
