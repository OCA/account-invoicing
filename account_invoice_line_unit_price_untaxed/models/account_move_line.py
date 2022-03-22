# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class AccountMoveLine(models.Model):

    _inherit = "account.move.line"

    price_unit_untaxed = fields.Float(
        compute="_compute_price_unit_untaxed",
        string="Price without Taxes",
        digits="Product Price",
        store=True,
    )

    @api.depends("product_id", "price_unit", "tax_ids")
    def _compute_price_unit_untaxed(self):
        """
        Use the compute_all method on tax to get the excluded price
        As this method uses the currency rounding and if price unit
        decimal precision is set to > currency one, the untaxed price
        can be too much rounded. So, use a memory record of currency
        with price unit decimal precision as rounding.
        """
        digits = self._fields["price_unit"].get_digits(self.env)
        rounding = (10 ** -digits[1]) if digits[1] else 0
        currencies = dict()
        for line in self:
            currency = line.move_id.currency_id
            if currency not in currencies:
                # Add the currency to saved ones in order to reuse it
                new_currency = self.env["res.currency"].new(
                    line.move_id.currency_id.copy_data()[0]
                )
                new_currency.rounding = rounding
                currencies[currency] = new_currency
            else:
                new_currency = currencies[currency]
            tot = line.tax_ids.compute_all(
                line.price_unit,
                currency=new_currency,
                quantity=1,
                product=line.product_id,
            )
            line.price_unit_untaxed = tot["total_excluded"]
