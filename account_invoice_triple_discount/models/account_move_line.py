# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import functools

from odoo import api, fields, models
from odoo.tools import float_compare


class AccountMoveLine(models.Model):

    _inherit = "account.move.line"

    discount2 = fields.Float(
        string="Discount 2 (%)",
        digits="Discount",
    )
    discount3 = fields.Float(
        string="Discount 3 (%)",
        digits="Discount",
    )

    @api.model_create_multi
    def create(self, values_list):
        """
        During the create of move lines, if the system detect that there is a
        difference between the balance and the price subtotal, it will update
        the unit price. When computing those, Odoo base module use a single
        discount on creation. So as there is a difference of the price given
        by the UI and the price computed during create method, the system will
        change the unit price of the invoice line. To avoid that, we update
        the discount field to have the aggregated discount, and we change it
        back after the creation.
        (Similar to _recompute_tax_lines on account.move)
        """
        old_values = []
        dp_discount = self.env["decimal.precision"].precision_get("Discount")
        for values in values_list:
            old_discount = values.get("discount", 0.0)
            new_discount = self._get_aggregated_discount_from_values(values)
            tmp_values = {}
            discount_changed = (
                float_compare(old_discount, new_discount, precision_digits=dp_discount)
                != 0
            )
            if discount_changed:
                values["discount"] = new_discount
                tmp_values["discount"] = old_discount
            old_values.append(tmp_values)
        records = super(AccountMoveLine, self).create(values_list)
        for index, record in enumerate(records):
            values = old_values[index]
            if values:
                record.write(old_values[index])
        return records

    @api.onchange(
        "discount",
        "price_unit",
        "tax_ids",
        "quantity",
        "discount2",
        "discount3",
    )
    def _onchange_price_subtotal(self):
        return super(AccountMoveLine, self)._onchange_price_subtotal()

    def _get_price_total_and_subtotal(self, **kwargs):
        self.ensure_one()
        kwargs["discount"] = self._compute_aggregated_discount(
            kwargs.get("discount") or self.discount
        )
        return super(AccountMoveLine, self)._get_price_total_and_subtotal(**kwargs)

    def _get_fields_onchange_balance(self, **kwargs):
        self.ensure_one()
        kwargs["discount"] = self._compute_aggregated_discount(
            kwargs.get("discount") or self.discount
        )
        return super(AccountMoveLine, self)._get_fields_onchange_balance(**kwargs)

    def _compute_aggregated_discount(self, base_discount):
        self.ensure_one()
        discounts = [base_discount]
        for discount_fname in self._get_multiple_discount_field_names():
            discounts.append(getattr(self, discount_fname, 0.0))
        return self._get_aggregated_multiple_discounts(discounts)

    def _get_aggregated_discount_from_values(self, values):
        discount_fnames = ["discount"]
        discount_fnames.extend(self._get_multiple_discount_field_names())
        discounts = []
        for discount_fname in discount_fnames:
            discounts.append(values.get(discount_fname) or 0.0)
        return self._get_aggregated_multiple_discounts(discounts)

    def _get_aggregated_multiple_discounts(self, discounts):
        discount_values = []
        for discount in discounts:
            discount_values.append(1 - (discount or 0.0) / 100.0)
        aggregated_discount = (
            1 - functools.reduce((lambda x, y: x * y), discount_values)
        ) * 100
        return aggregated_discount

    def _get_multiple_discount_field_names(self):
        return ["discount2", "discount3"]
